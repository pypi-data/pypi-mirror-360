import numpy as np
import pandas as pd
from scipy.stats import norm, nbinom
import scanpy as sc
from anndata import AnnData

def NBumiImputeNorm(counts, fit, total_counts_per_cell=None):
    """
    Normalizes data to a common library size, imputing zeros as needed.

    This function converts raw counts into positions in the CDF for the
    depth-adjusted negative binomial model fit to each observation. It adjusts
    the DANB parameters (mean and size) for the new library size. Then
    calculates the normalized counts for the equivalent position in the CDF
    for the NB using the new parameters.

    Parameters
    ----------
    counts : np.ndarray
        Raw count matrix, rows=genes, cols=cells.
    fit : dict
        Output from `NBumiFitModel`.
    total_counts_per_cell : float, optional
        Reference library size to normalize all cells to. If None, the median
        of the total counts per cell is used.

    Returns
    -------
    np.ndarray
        Normalized count matrix.
    """

    if total_counts_per_cell is None:
        total_counts_per_cell = np.median(fit['vals']['tis'])

    # Assuming NBumiFitDispVsMean and hidden_shift_size are available
    # These would need to be translated from the R code as well.
    # For now, let's assume they exist in some form.
    # A placeholder for NBumiFitDispVsMean
    def NBumiFitDispVsMean(fit, suppress_plot=True):
        vals = fit['vals']
        size_g = fit['sizes']
        forfit = (fit['size'] < np.max(size_g)) & (vals['tjs'] > 0) & (size_g > 0)
        higher = np.log2(vals['tjs'] / vals['nc']) > 4
        if np.sum(higher) > 2000:
            forfit = higher & forfit
        
        y = np.log(size_g[forfit])
        x = np.log((vals['tjs'] / vals['nc'])[forfit])
        
        # Using numpy's polyfit for linear regression (degree 1)
        coeffs = np.polyfit(x, y, 1)
        # In R's lm, the order is intercept, slope. np.polyfit is [slope, intercept]
        return coeffs[::-1] # Reverse to match R's coefficient order

    # A placeholder for hidden_shift_size
    def hidden_shift_size(mu_all, size_all, mu_group, coeffs):
        b = np.log(size_all) - coeffs[1] * np.log(mu_all)
        size_group = np.exp(coeffs[1] * np.log(mu_group) + b)
        return size_group

    coeffs = NBumiFitDispVsMean(fit, suppress_plot=True)
    vals = fit['vals']
    norm_mat = np.zeros_like(counts, dtype=float)
    normed_ti = total_counts_per_cell
    normed_mus = vals['tjs'] / vals['total']

    for i in range(counts.shape[0]):
        mu_is = vals['tjs'][i] * vals['tis'] / vals['total']
        
        # scipy.stats.nbinom.cdf is the equivalent of R's pnbinom
        # nbinom in scipy uses n (number of successes) and p (probability of success),
        # where size = n and mu = n*(1-p)/p.
        # We need to convert mu and size to n and p.
        # p = size / (size + mu)
        # n = size
        
        size = fit['sizes'][i]
        p_param = size / (size + mu_is)
        p_orig = nbinom.cdf(counts[i, :], n=size, p=p_param)

        new_size = hidden_shift_size(
            np.mean(mu_is), 
            fit['sizes'][i], 
            normed_mus[i] * normed_ti, 
            coeffs
        )
        
        new_mu = normed_mus[i] * normed_ti
        new_p_param = new_size / (new_size + new_mu)

        # scipy.stats.nbinom.ppf is the equivalent of R's qnbinom
        normed = nbinom.ppf(p_orig, n=new_size, p=new_p_param)
        norm_mat[i, :] = normed
        
    return norm_mat


def bg__filter_cells(expr_mat, labels=None, suppress_plot=False, min_detected_genes=None):
    """
    Internal function to filter cells based on the number of detected genes.
    """
    num_detected = np.sum(expr_mat > 0, axis=0)
    
    if min_detected_genes is not None:
        low_quality = num_detected < min_detected_genes
    else:
        num_zero = np.sum(expr_mat == 0, axis=0)
        cell_zero = num_zero
        mu = np.mean(cell_zero)
        sigma = np.std(cell_zero)
        
        # Deal with bi-modal
        if np.sum((cell_zero > mu - sigma) & (cell_zero < mu + sigma)) < 0.5 * len(cell_zero):
            mu = np.mean(cell_zero[cell_zero < np.median(cell_zero)])
            sigma = np.std(cell_zero[cell_zero < np.median(cell_zero)])
        
        p_vals = norm.sf(cell_zero, loc=mu, scale=sigma) # sf is 1 - cdf
        # A simple FDR implementation (Benjamini-Hochberg)
        p_vals_sorted = np.sort(p_vals)
        i = np.arange(1, len(p_vals) + 1)
        fdr_threshold = 0.05
        
        try:
            threshold_p = p_vals_sorted[p_vals_sorted <= i / len(p_vals) * fdr_threshold][-1]
            low_quality = p_vals <= threshold_p
        except IndexError:
            low_quality = np.repeat(False, len(p_vals))

    if np.sum(low_quality) > 0:
        if labels is not None and len(labels) == expr_mat.shape[1]:
            labels = labels[~low_quality]
        expr_mat = expr_mat[:, ~low_quality]
        
    return {'data': expr_mat, 'labels': labels}


def M3DropCleanData(expr_mat, labels=None, is_counts=True, suppress_plot=False, pseudo_genes=None, min_detected_genes=None):
    """
    Filters and normalizes an expression matrix.

    Removes low quality cells and undetected genes, and normalizes counts to
    counts per million.

    Parameters
    ----------
    expr_mat : np.ndarray or pd.DataFrame
        Raw or normalized (not log-transformed) expression values.
        Columns = samples/cells, rows = genes.
    labels : array-like, optional
        Vector of length equal to the number of columns of expr_mat with names
        or group IDs for each cell.
    is_counts : bool, default=True
        Whether the provided data is unnormalized read/fragment counts.
    suppress_plot : bool, default=False
        Whether to plot the distribution of number of detected genes per cell.
    pseudo_genes : list of str, optional
        Gene names of known pseudogenes which will be removed.
    min_detected_genes : int, optional
        Minimum number of genes/cell for a cell to be included.

    Returns
    -------
    dict
        A dictionary with 'data' (the normalized filtered expression matrix)
        and 'labels' (labels of the remaining cells).
    """
    if isinstance(expr_mat, pd.DataFrame):
        gene_names = expr_mat.index
        expr_mat_values = expr_mat.values
    else:
        expr_mat_values = expr_mat
        gene_names = None

    expr_mat_values[np.isnan(expr_mat_values)] = 0
    
    if pseudo_genes is not None and gene_names is not None:
        is_pseudo = gene_names.isin(pseudo_genes)
        expr_mat_values = expr_mat_values[~is_pseudo, :]
        gene_names = gene_names[~is_pseudo]

    data_list = bg__filter_cells(expr_mat_values, labels, suppress_plot, min_detected_genes)
    
    expr_mat_filtered = data_list['data']
    labels_filtered = data_list['labels']
    
    if gene_names is not None:
        # This assumes bg__filter_cells doesn't reorder genes
        gene_names_filtered = gene_names[np.sum(expr_mat_filtered > 0, axis=1) > 0]

    detected_genes = np.sum(expr_mat_filtered > 0, axis=1) > 3
    expr_mat_filtered = expr_mat_filtered[detected_genes, :]
    if gene_names is not None:
        gene_names_filtered = gene_names_filtered[detected_genes]

    if is_counts:
        # Spike-in logic from R code is complex, simplified here
        totreads = np.sum(expr_mat_filtered, axis=0)
        cpm = (expr_mat_filtered / totreads) * 1_000_000
        lowExpr = np.mean(cpm, axis=1) < 1e-5
        cpm = cpm[~lowExpr, :]
        if gene_names is not None:
            gene_names_filtered = gene_names_filtered[~lowExpr]
        
        if isinstance(expr_mat, pd.DataFrame):
             cpm = pd.DataFrame(cpm, index=gene_names_filtered, columns=labels_filtered)

        return {'data': cpm, 'labels': labels_filtered}

    lowExpr = np.mean(expr_mat_filtered, axis=1) < 1e-5
    data = expr_mat_filtered[~lowExpr, :]
    if gene_names is not None:
        gene_names_filtered = gene_names_filtered[~lowExpr]

    if isinstance(expr_mat, pd.DataFrame):
        data = pd.DataFrame(data, index=gene_names_filtered, columns=labels_filtered)
    
    return {'data': data, 'labels': labels_filtered}


def M3DropConvertData(input_data, is_log=False, is_counts=False, pseudocount=1):
    """
    Converts various data formats to a normalized, non-log-transformed matrix.

    Recognizes a variety of object types, extracts expression matrices, and
    converts them to a format suitable for M3Drop functions.

    Parameters
    ----------
    input_data : AnnData, pd.DataFrame, np.ndarray
        The input data.
    is_log : bool, default=False
        Whether the data has been log-transformed.
    is_counts : bool, default=False
        Whether the data is raw, unnormalized counts.
    pseudocount : float, default=1
        Pseudocount added before log-transformation.

    Returns
    -------
    np.ndarray
        A normalized, non-log-transformed matrix.
    """
    def remove_undetected_genes(mat):
        if isinstance(mat, pd.DataFrame):
            detected = mat.sum(axis=1) > 0
            print(f"Removing {np.sum(~detected)} undetected genes.")
            return mat[detected]
        else:
            detected = np.sum(mat, axis=1) > 0
            print(f"Removing {np.sum(~detected)} undetected genes.")
            return mat[detected, :]

    if isinstance(input_data, AnnData):
        if 'normcounts' in input_data.layers:
            return remove_undetected_genes(input_data.layers['normcounts'])
        elif 'logcounts' in input_data.layers:
            lognorm = input_data.layers['logcounts']
            norm = np.expm1(lognorm) if is_log else 2**lognorm - pseudocount
            return remove_undetected_genes(norm)
        elif input_data.X is not None:
             counts = input_data.X
        else:
            raise ValueError("AnnData object does not contain usable expression data.")
    elif isinstance(input_data, (pd.DataFrame, np.ndarray)):
        if is_log:
            lognorm = input_data
            norm = np.expm1(lognorm) if pseudocount == 0 else 2**lognorm - pseudocount
            return remove_undetected_genes(norm)
        elif is_counts:
            counts = input_data
        else:
            return remove_undetected_genes(input_data)
    else:
        raise TypeError(f"Unrecognized input format: {type(input_data)}")

    if 'counts' in locals():
        sf = np.sum(counts, axis=0)
        median_sf = np.median(sf)
        norm = (counts / sf) * median_sf
        return remove_undetected_genes(norm)
    
    raise ValueError("Could not process input data.")


def NBumiConvertToInteger(mat):
    """
    Converts an expression matrix to integer counts.

    Coerces the provided data to a matrix, rounds all values up (ceiling) to
    integers, and removes all rows where all values are zero.

    Parameters
    ----------
    mat : np.ndarray or pd.DataFrame
        A numeric matrix of expression values.

    Returns
    -------
    np.ndarray or pd.DataFrame
        Rounded, integer matrix of the original data.
    """
    if isinstance(mat, pd.DataFrame):
        mat_int = np.ceil(mat.values).astype(int)
        mat_df = pd.DataFrame(mat_int, index=mat.index, columns=mat.columns)
        mat_df = mat_df.loc[mat_df.sum(axis=1) > 0]
        return mat_df
    else:
        mat_int = np.ceil(mat).astype(int)
        mat_int = mat_int[np.sum(mat_int, axis=1) > 0, :]
        return mat_int


def NBumiConvertData(input_data, is_log=False, is_counts=False, pseudocount=1):
    """
    Converts various data formats to a count matrix for NBumi functions.

    Recognizes different object types, extracts expression matrices, and
    converts them to a count matrix.

    Parameters
    ----------
    input_data : AnnData, pd.DataFrame, np.ndarray
        The input data.
    is_log : bool, default=False
        Whether the data has been log-transformed.
    is_counts : bool, default=False
        Whether the data is raw, unnormalized counts.
    pseudocount : float, default=1
        Pseudocount added before log-transformation.

    Returns
    -------
    np.ndarray or pd.DataFrame
        A count matrix appropriate for input into NBumi functions.
    """
    def remove_undetected_genes(mat):
        if isinstance(mat, pd.DataFrame):
            detected = mat.sum(axis=1) > 0
            print(f"Removing {np.sum(~detected)} undetected genes.")
            return mat.loc[detected]
        else:
            detected = np.sum(mat, axis=1) > 0
            print(f"Removing {np.sum(~detected)} undetected genes.")
            return mat[detected, :]

    counts = None
    if isinstance(input_data, AnnData):
        if 'counts' in input_data.layers:
            counts = input_data.layers['counts']
        elif input_data.X is not None and (is_counts or not is_log):
             counts = input_data.X
        elif 'logcounts' in input_data.layers:
            lognorm = input_data.layers['logcounts']
        else:
            raise ValueError("AnnData object does not contain usable count or log-count data.")
    elif isinstance(input_data, (pd.DataFrame, np.ndarray)):
        if is_counts or not is_log:
            counts = input_data
        elif is_log:
            lognorm = input_data
    else:
        raise TypeError(f"Unrecognized input format: {type(input_data)}")
        
    if counts is not None:
        return NBumiConvertToInteger(remove_undetected_genes(counts))

    if 'lognorm' in locals():
        norm = 2**lognorm - pseudocount
        # Heuristic to convert back to counts
        sf = np.apply_along_axis(lambda x: np.min(x[x > 0]), 1, norm)
        sf = 1/sf
        counts = (norm.T / sf).T
        return NBumiConvertToInteger(remove_undetected_genes(counts))

    raise ValueError("Could not process input data.")


def NBumiPearsonResiduals(counts, fits=None):
    """
    Calculates Pearson Residuals using the NBumi depth-adjusted negative
    binomial model.

    Parameters
    ----------
    counts : np.ndarray
        Raw UMI counts matrix.
    fits : dict, optional
        The output from `NBumiFitModel`. If None, it will be computed.

    Returns
    -------
    np.ndarray
        Matrix of Pearson residuals.
    """
    if fits is None:
        # NBumiFitModel needs to be available
        # Placeholder for now
        from .utils import NBumiFitModel
        fits = NBumiFitModel(counts)
    
    mus = np.outer(fits['vals']['tjs'] / fits['vals']['total'], fits['vals']['tis'])
    sizes = fits['sizes'][:, np.newaxis] # Ensure sizes broadcasts correctly
    
    # Variance of NB is mu + mu^2/size
    variance = mus + (mus**2) / sizes
    pearson = (counts - mus) / np.sqrt(variance)
    return pearson


def NBumiPearsonResidualsApprox(counts, fits=None):
    """
    Approximates Pearson Residuals assuming a Poisson distribution.

    Parameters
    ----------
    counts : np.ndarray
        Raw UMI counts matrix.
    fits : dict, optional
        The output from `NBumiFitModel`. If None, some basic values will be computed.

    Returns
    -------
    np.ndarray
        Matrix of approximate Pearson residuals.
    """
    if fits is None:
        # Placeholder for hidden_calc_vals
        def hidden_calc_vals(cts):
            tjs = np.sum(cts, axis=1)
            tis = np.sum(cts, axis=0)
            total = np.sum(tjs)
            return {'tjs': tjs, 'tis': tis, 'total': total}
        vals = hidden_calc_vals(counts)
    else:
        vals = fits['vals']
    
    mus = np.outer(vals['tjs'] / vals['total'], vals['tis'])
    pearson = (counts - mus) / np.sqrt(mus)
    return pearson
