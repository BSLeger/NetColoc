# -*- coding: utf-8 -*-

'''Functions for performing network localization
'''

# External library imports
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm.auto import tqdm

# Internal module convenience imports
from .netcoloc_utils import *

def __init__(self):
    pass

# -------------------- LOCALIZATION ---------------------------------#

def netprop_localization(z_scores, random_final_heats, seed_genes, z_score_threshold=3, plot=True):
    '''Calculates the size of a gene set's network proximity based on the
    z-score results of network propagation, and evaluates if it is larger than
    chance by repeating the algorithm using random degree-matched seed genes.
    Returns a z-score.

    Args:
        z_scores (pandas.Series): The output of the
            netprop_zscore.netprop_zscore() method. A pandas Series where the
            index contains gene names, and the data contains the z-scores
            associated with each gene after network propagation.
        random_final_heats (numpy.ndarray): The output of the
            netprop_zscore.netprop_zscore() method. A matrix containing
            z_scores, where each column corresponds to a gene, and each row
            corresponds to a network propagation performed using random seed
            genes.
        seed_genes (list): The list of seed genes used to generate the z_scores
            and random_final_heats arguments.
        z_score_threshold (float): The threshold after which genes are
            considered significantly proximal to each other. (Default: 3)
        save_localization_scores (bool): If True, then the results of the random
            localization trials will be saved as a tsv file in the current
            directory. If False, the file will not be saved. (Default: False)
        plot (bool): If True, then the distribution will be plotted. If False,
            it will not be plotted. (Default: False)

    Returns:
        float: The z-score representing how much larger the network proximity of
            this seed gene is than would be expected by chance.
    '''
    nan_row = [np.nan] * len(random_final_heats[0])

    random_proximal_network_sizes = []
    for row in tqdm(range(len(random_final_heats))):
        # Calculate mean and standard deviation, excluding focal row
        focal_row = random_final_heats[row]
        random_final_heats[row] = nan_row
        mean = np.nanmean(np.log(random_final_heats), axis=0)
        standard_deviation = np.nanstd(np.log(random_final_heats), axis=0)
        # Calculate z-scores for each gene in random network
        random_z_score = (np.log(focal_row) - mean) / standard_deviation
        # Count gene in proximal network, not including seed genes
        random_proximal_network_sizes.append(sum(random_z_score > z_score_threshold) - len(seed_genes))
        # Replace focal row in random final heats matrix
        random_final_heats[row] = focal_row

    # Calculate the size of the true proximal subgraph, not including seed genes
    proximal_network_size = sum(z_scores > z_score_threshold) - len(seed_genes)

    # Calculate z-score
    z_score = (np.log(proximal_network_size) - np.nanmean(np.log(random_proximal_network_sizes))) / np.nanstd(np.log(random_proximal_network_sizes))

    #TODO: clean this up (ymax)
    if plot:
        plt.figure(figsize=(5, 4))
        dfig = sns.distplot(random_proximal_network_sizes, label='random', kde=False)
        plt.vlines(proximal_network_size, ymin=0, ymax=dfig.dataLim.bounds[3], color='r', label='True gene set')
        plt.xlabel('Size of proximal network, z > ' + str(z_score_threshold), fontsize=16)
        plt.ylabel('Count', fontsize=16) 
        plt.legend(loc='upper left')

    return z_score, proximal_network_size, random_proximal_network_sizes, 