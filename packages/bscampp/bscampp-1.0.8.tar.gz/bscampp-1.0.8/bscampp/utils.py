#from dendropy import *
import numpy as np
import heapq
import treeswift
import itertools
from collections import deque
from os.path import expanduser,isfile
import random
import statistics
import copy
import gzip
import argparse

from bscampp import get_logger, log_exception
_LOG = get_logger(__name__)

# reformat argparse help text formatting
class SmartHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_text(self, text):
        if text is not None:
            text = text.replace("\\n", "\n").replace("\\t", "\t")
        super().add_text(text)
    def _split_lines(self, text, width):
        if '\n' in text:
            temp = text.split('\n')
            ret = []
            for _splice in [argparse.RawDescriptionHelpFormatter._split_lines(self, x, width)
                    for x in temp]:
                ret.extend(_splice)
            return ret
        return argparse.RawDescriptionHelpFormatter._split_lines(self, text, width)

# store bracket open/close for convenience in label parsing
BRACKET = {
    '[': ']', # square bracket
    '{': '}', # curly bracket
    "'": "'", # single-quote
    '"': '"', # double-quote
}


# infer datatype from input file
def inferDataType(path):
    sequences = read_data(path)
    acg, t, u, total = 0, 0, 0, 0
    for taxon, seq in sequences.items():
        letters = seq.upper()
        for letter in letters:
            total = total + 1

            if letter in ('A', 'C', 'G', 'N'):
                acg += 1
            elif letter == 'T':
                t += 1
            elif letter == 'U':
                u += 1
    # dna -> nucleotide
    if u == 0 and (acg + t) / total > 0.9:
        datatype = 'nucleotide'
    # rna -> nucleotide
    elif t == 0 and (acg + u) / total > 0.9:
        datatype = 'nucleotide'
    # amino acid -> protein
    else:
        datatype = 'protein'

    _LOG.info(f"Inferred input data type: {datatype}")
    return datatype

def write_fasta(aln, aln_dict, aligned=True):
    """ Write given dictionary as FASTA file out
    
    Parameters
    ----------
    aln : FASTA file path
    aln_dict : MSA in the form of a dict
    aligned : whether the sequences are aligned

    Returns
    -------
    None

    """

    f = open(aln, 'w')
    for label, seq in aln_dict.items():
        if label != '':
            f.write(f'>{label}\n')
            if aligned:
                f.write(f'{seq}\n')
            else:
                f.write(seq.replace('-', '') + '\n')
    f.close()

#separete the query and ref sequence from the alignment file

def read_data(aln):
    """ Load the query and reference sequence from the alignment file
    
    Parameters
    ----------
    aln : multiple sequence alignment containing reference taxa and query sequence
    
    Returns
    -------
    dictionary containing sequences with taxon label keys
    
    """

    # determine the file type, whether we have a .gz/.gzip file
    suffix = aln.split('.')[-1]
    if suffix in ['gz', 'gzip']:
        f = gzip.open(aln, 'rt')
    else:
        f = open(aln)
    result = dict()

    taxa = ""
    seq = ""
    for line in f:
        if line[0] == '>':
            if taxa != "":
                result[taxa] = seq
            taxa = line[1:-1]
            seq = ""

        elif line == "/n":
            continue
        else:
            seq += line[:-1]

    if taxa != "":
        result[taxa] = seq


    return result

def seperate(aln_dict, leaf_dict):
    """ Separate the query sequences from the reference sequences
    
    Parameters
    ----------
    aln_dict : Sequence dictionary with taxon label keys
    leaf_dict : Sequence dictionary with leaf label keys (queries are not in backbone tree)
    
    Returns
    -------
    separate dictionaries containing query sequences and referece sequences with taxon label keys
    
    """
    ref = dict()
    query = dict()

    for key, value in aln_dict.items():
        if key not in leaf_dict:
            query[key] = value
        else:
            ref[key] = value

    return ref, query

def hamming(seq1, seq2):
    """ Returns hamming distance between two sequences
    
    Parameters
    ----------
    seq1 : query sequence
    seq2 : reference sequence
    
    Returns
    -------
    integer hamming distance between query sequence and reference sequence
    
    """
    return sum(1 for ch1, ch2 in zip(seq1, seq2) if ch1 != ch2)


def find_y(x,ref):
    """ Returns leaf label for closest sister taxon l (no longer used)
    
    Parameters
    ----------
    x : aligned query sequence
    ref : reference multiple sequence alignment dictionary 
    
    Returns
    -------
    leaf label for taxon with smallest hamming distacne to query sequence
    
    """
    low = len(x)
    y = ""
    for name, seq in ref.items():
        h_dist = hamming(x, seq)
        if h_dist < low:
            low = h_dist
            y = name
    return y

def set_hamming_dict(args):
    dict_items, other_args = args
    name, seq = dict_items
    ref, n, fragment_flag, y_dict = other_args
    
    y_dict[name] = find_closest_hamming(seq, ref, n, fragment_flag)


def find_closest_hamming(x, ref, n, fragment_flag):
    ''' Returns leaf name for n closest sister taxa to sequence x
    
    Parameters
    ----------
    x : aligned query sequence
    ref : reference multiple sequence alignment dictionary 
    n : number of nodes to return 
    fragment_flag : True if the query is not full length
    
    Returns
    -------
    list of nodes with n smallest hamming distacnes to query sequence

    '''
    queue = []
    closest = []

    counter = 0
    if fragment_flag == 'True':
        [si, ei] = set_fragment_indicies(x)
    else:
        [si, ei] = [0, len(x)]
    
    c = 200 # size of the subtring compared at once
        
    for name, seq in ref.items():
        heapq.heappush(queue,(hamming(seq[si:si+c],x[si:si+c]), ei - si - c, counter, name))
        counter += 1

    while queue:
        (ham_dist, sites_left, cnt, name) = heapq.heappop(queue)
        if sites_left < 0:
            closest.append(name)
            if len(closest) >= n:
                return closest
        else:
            ind = ei - sites_left
            new_ham = hamming(ref[name][ind:ind+c],x[ind:ind+c])
            heapq.heappush(queue,(ham_dist + new_ham, sites_left - c, cnt, name))

def set_fragment_indicies(x):
    """ Returns the indicees without leading and trailing gaps.
    
    Parameters
    ----------
    x = string sequence
    
    Returns
    -------
    list of start index and end index with the first and last non gap character
    
    """
    e = len(x)
    ei = e
    si = 0
    for i in range(ei): 
        if x[i] == '-' and si == i:
            si = i + 1
        if x[e - i - 1] == '-' and ei == e - i:
            ei = e - i - 1
        if ei == si:
            break
    return [si, ei] 

def find_closest(x, visited, y=None):
    """ Returns leaf label for closest leaf to the node x through path not travelling through visited.
    If y is populated returns path from x to y not travelling through nodes in visited.
    
    Parameters
    ----------
    x : dendropy node object
    visited : dictionary containing dendropy node objects as keys 
    y : dendropy node object
    
    Returns
    -------
    If y == None : dendropy node object of closest leaf y to the node x through path not travelling through nodes in visited, 
                   list containing dendropy node objects on path to that leaf y from node x
    If y != None : dendropy node object y, 
                   list containing dendropy node objects on path from node x to leaf y not travelling through nodes in visited
    
    """
    queue = []
    cnt = 1
    visited.add(x)

    if x.get_parent() and x.get_parent() not in visited:
        tmp = []
        tmp.append(x)
        heapq.heappush(queue, [x.get_edge_length(), cnt, tmp, x.get_parent()])
        cnt += 1

    for child in x.child_nodes():
        if child and child not in visited:
            tmp = []
            tmp.append(child)
            heapq.heappush(queue, [child.get_edge_length(), cnt, tmp, child])
            cnt += 1

    while len(queue) > 0:
        try:
            [length, _, path, node] = heapq.heappop(queue)
        except IndexError:
            break

        visited.add(node)
        if node.is_leaf():
            if (not y) or node.get_label()==y.get_label():
                return node, path
            else:
                continue

        if node.get_parent() and node.get_parent() not in visited:
            tmp = path.copy()
            tmp.append(node)
            heapq.heappush(queue, [length+node.get_edge_length(), cnt, tmp, node.get_parent()])
            cnt += 1

        for child in node.child_nodes():
            if child and child not in visited:
                tmp = path.copy()
                tmp.append(child)
                heapq.heappush(queue, [length+child.get_edge_length(), cnt, tmp, child])
                cnt += 1

    return x, [x]


def find_closest_testing(x, visited, y=None, valid_leaves=None):
    """ Returns leaf label for closest leaf to the node x through path not travelling through visited.
    If y is populated returns path from x to y not travelling through nodes in visited.
    
    Parameters
    ----------
    x : dendropy node object
    visited : dictionary containing dendropy node objects as keys
    y : dendropy node object
    
    Returns
    -------
    If y == None : dendropy node object of closest leaf y to the node x through path not travelling through nodes in visited, 
                   list containing dendropy node objects on path to that leaf y from node x
                   distance from node x to leaf y
    If y != None : dendropy node object y, 
                   list containing dendropy node objects on path from node x to leaf y not travelling through nodes in visited, 
                   distance from node x to leaf y
    
    """
    queue = []
    cnt = 1
    visited.add(x)

    if x.get_parent() and x.get_parent() not in visited:
        tmp = []
        tmp.append(x)
        heapq.heappush(queue, [x.get_edge_length(), cnt, tmp, x.get_parent()])
        cnt += 1

    for child in x.child_nodes():
        if child and child not in visited:
            tmp = []
            tmp.append(child)
            heapq.heappush(queue, [child.get_edge_length(), cnt, tmp, child])
            cnt += 1

    while len(queue) > 0:
        try:
            [length, _, path, node] = heapq.heappop(queue)
        except IndexError:
            break

        visited.add(node)
        if node.is_leaf():
            if (not y) or node.get_label() == y.get_label():
                if  (valid_leaves != None and node.get_label() not in valid_leaves):
                    continue
                else:
                    return node, path, length
            else:
                continue

        if node.get_parent() and node.get_parent() not in visited:
            tmp = path.copy()
            tmp.append(node)
            heapq.heappush(queue, [length+node.get_edge_length(), cnt, tmp, node.get_parent()])
            cnt += 1

        for child in node.child_nodes():
            if child and child not in visited:
                tmp = path.copy()
                tmp.append(child)
                heapq.heappush(queue, [length+child.get_edge_length(), cnt, tmp, child])
                cnt += 1

    return x, [x], 0

def build_subtrees(sister_taxon_dict, leaf_dict, tree, nbr_subtrees, subtree_size):
    tree_building_taxa = len(list(sister_taxon_dict))
    cluster_dict = dict()
    cluster_index = 0 
    cluster_list = dict()
    
    

    #tmp
    #draw(tree.extract_tree_with(list(sister_taxon_dict)))
    #tmp

    for taxon, _ in sister_taxon_dict.items():
        cluster_dict[taxon] = cluster_index
        cluster_list[cluster_index] = [taxon]
        cluster_index += 1

    queue = []
    for l1, _ in sister_taxon_dict.items():
        node_l2, _, length = find_closest_testing(leaf_dict[l1],{leaf_dict[l1]},valid_leaves=sister_taxon_dict)
        heapq.heappush(queue, [length, l1, node_l2.get_label()])

    while tree_building_taxa > nbr_subtrees:        
        [length, l1, l2] = heapq.heappop(queue)

        idx = cluster_dict[l1]
        old_idx = cluster_dict[l2]

        if idx == old_idx:
            continue

        for leaf in cluster_list[old_idx]:
            cluster_dict[leaf] = idx
        #[cluster_dict[leaf] = idx for leaf in cluster_list[old_idx]]
        cluster_list[idx].extend(cluster_list[old_idx])
        cluster_list.pop(old_idx)

        tree_building_taxa -= 1

        best_leaf = cluster_list[idx][0]
        for leaf in cluster_list[idx]:
            best_leaf = centered_leaf(tree, cluster_list[idx])
        cluster_node_list = [leaf_dict[leaf] for leaf in cluster_list[idx]]
        cluster_set = {*cluster_node_list}
        node_l3, _, length = find_closest_testing(leaf_dict[best_leaf], cluster_set, valid_leaves=sister_taxon_dict)
        heapq.heappush(queue, [length, best_leaf, node_l3.get_label()])

    trees = []
    query_decomp_dict = []

    for idx, cluster in cluster_list.items():
        best_leaf = centered_leaf(tree, cluster)

        subtree_leaves, tree2 = subtree_with_edge_length(tree, leaf_dict[best_leaf], subtree_size)
        tree2 = tree2.extract_tree_with(subtree_leaves)
        trees.append(tree2)
        query_list = []
        for leaf in cluster:
            query_list.extend(sister_taxon_dict[leaf])
        query_decomp_dict.append(query_list)

    return trees, query_decomp_dict


def subtree_nodes(tree, leaf_y, n):
    """ Returns list of length n of leaves closest to sister taxon
    
    Parameters
    ----------
    tree : treeswift tree object
    leaf_y : treeswift node for closest sister taxon
    n = number of taxa contained in subtree
    
    Returns
    -------
    list of taxon labels corresponding to leaves in the subtree
    
    """
    queue = [(0, 0, leaf_y.get_parent())]

    leaves = [leaf_y]
    visited = {leaf_y}

    counter = 1

    while len(leaves) < n:
        try:
            (length, _, node) = heapq.heappop(queue)
        except IndexError:
            break

        visited.add(node)
        if node.is_leaf():
            leaves.append(node)

        adjacent = node.child_nodes()
        if not node.is_root():
            adjacent.append(node.get_parent())

        for neighbor in adjacent:
            if neighbor not in visited:
                heapq.heappush(queue, (length+1, counter, neighbor))
                counter += 1


    result = []
    for item in leaves:
        result.append(item.get_label())

    return result

def subtree_nodes_with_edge_length(tree, leaf_y, n):
    """ Returns list of length n of leaves closest to sister taxon (minimizing edge weights)
    
    Parameters
    ----------
    tree : treeswift tree object
    leaf_y : treeswift node for closest sister taxon
    n = number of taxa contained in subtree
    
    Returns
    -------
    list of taxon labels corresponding to leaves in the subtree
    """
    queue = [(leaf_y.get_edge_length(), leaf_y.get_parent())]

    leaves = [leaf_y]
    visited = {leaf_y}

    while len(leaves) < n:
        try:
            (length, node) = heapq.heappop(queue)
        except IndexError:
            break

        visited.add(node)
        if node.is_leaf() and node.get_label() != '':
            leaves.append(node)

        adjacent_nodes = node.child_nodes()
        if not node.is_root():
            adjacent_nodes.append(node.get_parent())

        for neighbor in adjacent_nodes:
            if neighbor not in visited:
                if neighbor == node.get_parent():
                    heapq.heappush(queue, (length+node.get_edge_length(), neighbor))
                else:
                    heapq.heappush(queue, (length+neighbor.get_edge_length(), neighbor))

    result = []
    for item in leaves:
        result.append(item.get_label())

    return result
    
def subtree_with_edge_length(tree, leaf_y, n):
    """ Returns a subtree and list of length n of leaves closest to sister taxon (minimizing edge weights)
    
    Parameters
    ----------
    tree : treeswift tree object
    leaf_y : treeswift node for closest sister taxon
    n = number of taxa contained in subtree
    
    Returns
    -------
    a subtree and a list of taxon labels corresponding to leaves in the subtree
    """
    if leaf_y.get_parent() == None:
        return None, None
    
    subtree = treeswift.Tree(); subtree.root.label = None; subtree.root.edge_length = 0
    subtreeNode = treeswift.Node(label=leaf_y.get_label(), edge_length=0); subtree.root.add_child(subtreeNode)
        
    queue = [(leaf_y.get_edge_length(), leaf_y.get_parent(), leaf_y.get_edge_length(), subtree.root)]

    leaves = [leaf_y]
    visited = {leaf_y}

    while len(leaves) < n:
        try:
            (length, node, n_edge_length, parent) = heapq.heappop(queue)
        except IndexError:
            break

        visited.add(node)
        subtreeNode = treeswift.Node(label=node.get_label(), edge_length=n_edge_length); parent.add_child(subtreeNode)
        if node.is_leaf():
            leaves.append(node)

        adjacent_nodes = node.child_nodes()
        if not node.is_root():
            adjacent_nodes.append(node.get_parent())

        for neighbor in adjacent_nodes:
            if neighbor not in visited:
                if neighbor == node.get_parent():
                    heapq.heappush(queue, (length+node.get_edge_length(), neighbor, node.get_edge_length(), subtreeNode))
                else:
                    heapq.heappush(queue, (length+neighbor.get_edge_length(), neighbor, neighbor.get_edge_length(), subtreeNode))

    result = []
    for item in leaves:
        result.append(item.get_label())
    
    #subtree.deroot()
    subtree.suppress_unifurcations()
    return result, subtree
    
def extract_taxa_from_tree(a_tree, labels, leaf_dict):
    queue = []
    closest = []

    counter = 0
        
    for label in labels: 
        heapq.heappush(queue,(counter,leaf_dict[label]))
        counter += 1

    while queue:
        (cnt, node) = heapq.heappop(queue)
        if node.num_children() == 0:
            parent = node.get_parent()
            if parent != None:
                parent.remove_child(node)
                heapq.heappush(queue,(counter, parent))
    
    a_tree.resolve_polytomies()            
    a_tree.suppress_unifurcations()

    return a_tree
    
def min_tree_extract_disjoint(a_tree, max_size, tmp_leaves):
    labels, t2 = subtree_with_edge_length(a_tree, tmp_leaves[random.choice(list(tmp_leaves))], max_size)
    
    t2 = t2.extract_tree_with(labels)
    t1 = extract_taxa_from_tree(a_tree, labels, tmp_leaves)
    for label in labels:
       del tmp_leaves[label]
    return t1, t2, tmp_leaves

    
def min_tree_extract_non_disjoint(a_tree, max_size, tmp_leaves):
    labels, t2 = subtree_with_edge_length(a_tree, tmp_leaves[random.choice(list(tmp_leaves))], max_size)
    
    t2 = a_tree.extract_tree_with(labels)
    for label in labels:
       if label in tmp_leaves:
           del tmp_leaves[label]
    return a_tree, t2, tmp_leaves
    
def decompose_tree(a_tree,max_size):
    tree_list = []
    tmp_leaves = a_tree.label_to_node(selection='leaves')
    if '' in tmp_leaves:
        del tmp_leaves['']
    #t1, t2, tmp_leaves = min_tree_extract_disjoint(a_tree, max_size, tmp_leaves)
    t1, t2, tmp_leaves = min_tree_extract_non_disjoint(a_tree, max_size, tmp_leaves)
    while len(tmp_leaves) > 0:
        tree_list.append(t2)

        #t1, t2, tmp_leaves = min_tree_extract_disjoint(t1, max_size, tmp_leaves)
        t1, t2, tmp_leaves = min_tree_extract_non_disjoint(t1, max_size, tmp_leaves)
    tree_list.append(t2)
    print ("nbr subtrees: ", len(tree_list))
    return tree_list
    
def decompose_tree_min_clust(a_tree,max_size):
    tree_list = []
    t1, t2 = min_cluster_size_bisect(a_tree,max_size)
    while t2 != None:
        tree_list.append(t2)
        t1, t2 = min_cluster_size_bisect(t1, max_size)
    tree_list.append(t1) #this might be a bug
    return tree_list    
    
def min_cluster_size_bisect(a_tree,max_size):
    '''
    modified from PASTA to use treeswift
    '''
    nleaf = dict()

    print("before extracting subtree: " + str(len(a_tree.label_to_node(selection='leaves'))))
    #a_tree.draw()
    
    for node in a_tree.traverse_postorder():
        if node.is_leaf():
            nleaf[node] = 1
        else:
            nleaf[node] = 0
            max_child = None
            max_nleaf = 0
            for ch in node.child_nodes():
               nleaf[node] += nleaf[ch]
               if nleaf[ch] > max_nleaf:
                   max_nleaf = nleaf[ch]
                   max_child = ch
        if nleaf[node] >= max_size:
            node.remove_child(max_child)
            t1 = a_tree.extract_subtree(max_child)
            print("subtree size:              " + str(len(t1.label_to_node(selection='leaves'))))
            print("after extracting subtree:  " + str(len(a_tree.label_to_node(selection='leaves'))))
            #t1.deroot()
            #t1.draw()
            t1.resolve_polytomies()
            return a_tree,t1
    
    print("after extracting subtree:  " + str(len(a_tree.label_to_node(selection='leaves'))))
    return a_tree,None      

def centered_leaf(tree, cluster):
    #pick best sister leaf for cluster center
    best_leaf = cluster[0]
    if len(cluster) > 1:
        tmp_tree = tree.extract_tree_with(cluster)
        min_distance = 99999999999
        tmp_label_dict = tmp_tree.label_to_node(selection='leaves')
        for leaf in cluster: 
            total = total_distance(tmp_tree, tmp_label_dict[leaf])

            if total < min_distance:
                min_distance = total
                best_leaf = leaf

    return best_leaf

def max_distance(tree, node):
    maximum = 0 
    for leaf in tree.traverse_leaves():
        distance = tree.distance_between(node, leaf)
        if distance >= maximum:
            maximum = distance
    return maximum

def total_distance(tree, node):
    total = 0 
    for leaf in tree.traverse_leaves():
        total += tree.distance_between(node, leaf)
    return total


def avg_distance(tree, node):
    total = 0 
    leaf_cnt = 0
    for leaf in tree.traverse_leaves():
        total += tree.distance_between(node, leaf)
        leaf_cnt += 1
    return total/leaf_cnt

def median_distance(tree, node):
    total = 0
    leaf_cnt = 0
    distances = []
    for leaf in tree.traverse_leaves():
        distance = tree.distance_between(node, leaf)
        total += distance
        distances.append(distance)
        leaf_cnt += 1
    return statistics.median(distances)

def add_edge_nbrs(tree):
    counter = 0
    for node in tree.traverse_postorder():
        #if not node.is_root():
            counter += 1
            label = node.get_label()
            if label == None:
                node.set_label('%%{}'.format(counter))
            else:
                node.set_label('{}%%{}'.format(label, counter))

def remove_edge_nbrs(tree):
    for node in tree.traverse_postorder():
        #if not node.is_root():
            label_list = node.get_label().split('%%',1)
            if label_list[0] == '':
                node.set_label(None)
            else:
                node.set_label(label_list[0])

'''
   The following three functions are modified from treeswift to
   read and write newick files with jplace tokens
'''
def newick_edge_tokens(tree):
    '''
    Modified from treeswift tree.newick()
    Output this ``Tree`` as a Newick string with lables
    Returns:
        ``str``: Newick string of this ``Tree``
    '''
    label_list = tree.root.get_label().split('%%',1)

    if tree.root.edge_length is None:
        suffix = ';'
    elif isinstance(tree.root.edge_length,int):
        suffix = '%s:%d{%d};' % (str(label_list[0]), int(tree.root.edge_length), int(label_list[1]))
    elif isinstance(tree.root.edge_length,float) and tree.root.edge_length.is_integer():
        suffix = '%s:%d{%d};' % (str(label_list[0]), float(tree.root.edge_length), int(label_list[1]))
    else:
        suffix = '%s:%s{%d};' % (str(label_list[0]), str(tree.root.edge_length), int(label_list[1]))

    if tree.is_rooted:
        return '[&R] %s%s' % (newick_edge_tokens_node(tree.root),suffix)
    else:
        return '%s%s' % (newick_edge_tokens_node(tree.root),suffix)

def newick_edge_tokens_node(node):
    '''
    Modified from treeswift node.newick()
    Newick string conversion starting at this ``Node`` object
    Returns:
        ``str``: Newick string conversion starting at this ``Node`` object
    '''
    node_to_str = dict()
    for node in node.traverse_postorder():
        node_label = node.get_label()
        [label, edge_nbr] = node_label.split('%%',1)
        #node.set_label(label_list[0])
        if node.is_leaf():
            if label is None:
                node_to_str[node] = ''
            else:
                node_to_str[node] = str(label)
        else:
            out = ['(']
            for c in node.children:
                c_label = c.get_label()
                [label_c, edge_nbr_c] = c_label.split('%%',1)
                out.append(node_to_str[c])
                if c.edge_length is not None:
                    if isinstance(c.edge_length,int):
                        l_str = str(c.edge_length)
                    elif isinstance(c.edge_length,float) and c.edge_length.is_integer():
                        l_str = str(int(c.edge_length))
                    else:
                        l_str = str(c.edge_length)
                    out.append(':%s{%d}' % (l_str, int(edge_nbr_c)))
                out.append(',')
                del node_to_str[c]
            out.pop() # trailing comma
            out.append(')')
            if label is not None:
                out.append(str(label))
            node_to_str[node] = ''.join(out)
    return node_to_str[node]

#def write_tree_newick_edge_tokens(tree, filename, hide_rooted_prefix=False):
#    '''
#    Modified from treeswift tree.write_tree_newick()
#    Write this ``Tree`` to a Newick file
#       Args:
#        ``filename`` (``str``): Path to desired output file (plain-text or gzipped)
#    '''
#    if not isinstance(filename, str):
#        raise TypeError("filename must be a str")
#    treestr = newick_edge_nbr_string(tree)
#    if hide_rooted_prefix:
#        if treestr.startswith('[&R]'):
#            treestr = treestr[4:].strip()
#    else:
#        warn("Specified hide_rooted_prefix, but tree was not rooted")
#    if filename.lower().endswith('.gz'): # gzipped file
#        f = gopen(expanduser(filename),'wb',9); f.write(treestr.encode()); f.close()
#    else: # plain-text file
#        f = open(expanduser(filename),'w'); f.write(treestr); f.close()

def read_tree_newick_edge_tokens(newick):
    '''
    Modified from treeswift.read_tree_newick(newick)
    Read a tree from a Newick string or file
    Args:
        ``newick`` (``str``): Either a Newick string or the path to a Newick file (plain-text or gzipped)

    Returns:
        ``Tree``: The tree represented by ``newick``. If the Newick file has multiple trees (one per line), a ``list`` of ``Tree`` objects will be returned
    '''
    place_edge_dict = dict()
    if not isinstance(newick, str):
        try:
            newick = str(newick)
        except:
            raise TypeError("newick must be a str")
    if newick.lower().endswith('.gz'): # gzipped file
        f = gzip.open(expanduser(newick)); ts = f.read().decode().strip(); f.close()
    elif isfile(expanduser(newick)): # plain-text file
        f = open(expanduser(newick)); ts = f.read().strip(); f.close()
    else:
        ts = newick.strip()
    lines = ts.splitlines()
    if len(lines) != 1:
        return [read_tree_newick_edge_tokens(l) for l in lines]
    try:
        t = treeswift.Tree(); t.is_rooted = ts.startswith('[&R]')
        if ts[0] == '[':
            ts = ']'.join(ts.split(']')[1:]).strip(); ts = ts.replace(', ',',')
        n = t.root; i = 0
        while i < len(ts):
            # end of Newick string
            if ts[i] == ';':
                if i != len(ts)-1 or n != t.root:
                    raise RuntimeError("INVALID NEWICK")

            # go to new child
            elif ts[i] == '(':
                c = treeswift.Node(); n.add_child(c); n = c

            # go to parent
            elif ts[i] == ')':
                n = n.parent

            # go to new sibling
            elif ts[i] == ',':
                n = n.parent; c = treeswift.Node(); n.add_child(c); n = c

            # edge length
            elif ts[i] == ':':
                i += 1; ls = ''
                while ts[i] != ',' and ts[i] != ')' and ts[i] != ';' and ts[i] != '{':
                    ls += ts[i]; i += 1
                if ls[0] == '[':
                    n.edge_params = ']'.join(ls.split(']')[:-1]); ls = ls.split(']')[-1]
                n.edge_length = float(ls); i -= 1

            # edge token
            elif ts[i] == '{':
                i += 1; ls = ''
                while ts[i] != '}':
                    ls += ts[i]; i += 1
                place_edge_dict[ls] = n

            # node label
            else:
                label = ''; bracket = None
                while bracket is not None or ts[i] in BRACKET or (ts[i] != ':' and ts[i] != ',' and ts[i] != ';' and ts[i] != ')'):
                    if ts[i] in BRACKET and bracket is None:
                        bracket = ts[i]
                    elif bracket is not None and ts[i] == BRACKET[bracket]:
                        bracket = None
                    label += ts[i]; i += 1
                i -= 1; n.label = label
            i += 1
    except Exception as e:
        raise RuntimeError("Failed to parse string as Newick")
    return t, place_edge_dict
