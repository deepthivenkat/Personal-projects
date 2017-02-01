from sklearn import metrics
from sklearn.metrics import pairwise_distances
from sklearn import datasets
from texttable import Texttable
from sklearn.cluster import KMeans
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.cluster import DBSCAN
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import numpy as np
from scipy.sparse.csgraph import connected_components
import Cluster_Ensembles as CE

def create_coassociation_matrix(labels):
	rows = []
	cols = []
	unique_labels = set(labels)
	for label in unique_labels:
                arr = np.array(labels)
		indices = np.where(arr == label)[0]
		for index1 in indices:
			for index2 in indices:
				rows.append(index1)
				cols.append(index2)
	data = np.ones((len(rows),))
	return csr_matrix((data, (rows, cols)), dtype='float')

class EAC(BaseEstimator, ClusterMixin):
        def __init__(self, n_clusterings=10, cut_threshold=0.5, n_clusters_range=(3, 10)):
                self.n_clusterings = n_clusterings
                self.cut_threshold = cut_threshold
                self.n_clusters_range = n_clusters_range
                
        
        def _single_clustering(self,X):
                n_clusters = np.random.randint(*self.n_clusters_range)
                km = KMeans(n_clusters=n_clusters)
                return km.fit_predict(X)

        def fit(self, X, y=None):
                C = sum((create_coassociation_matrix(self._single_clustering(X)) for i in range(self.n_clusterings)))
                mst = minimum_spanning_tree(-C)
                print mst
                mst.data[mst.data > -self.cut_threshold] = 0
                self.n_components, self.labels_ = connected_components(mst)
                return self

labels = []
dataset = datasets.load_iris()
X = dataset.data
y = dataset.target
bandwidth = estimate_bandwidth(X, quantile=0.2, n_samples=500)
kmeans_model = KMeans(n_clusters=3, random_state=1).fit(X)
af = AffinityPropagation(preference=-50).fit(X)
ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
ms.fit(X)
db = DBSCAN(eps=0.3, min_samples=10).fit(X)
cluster_centers_indices = af.cluster_centers_indices_
labels_af = af.labels_
labels_km = kmeans_model.labels_
labels_mf = ms.labels_
labels_db = db.labels_
evidence_accum = EAC()
labels_ea = evidence_accum.fit(X).labels_


t = Texttable()
t.add_rows([['Algorithms', 'Calinski-Harabaz Index', 'Silhouette Coefficient', 'Fowlkes-Mallows scores', 'Homogeneity, completeness and V-measure', 'Adjusted Rand index', 'Mutual Information based scores'], ['K-means', metrics.calinski_harabaz_score(X, labels_km), metrics.silhouette_score(X, labels_km, metric='euclidean'), metrics.fowlkes_mallows_score(y, labels_km), metrics.homogeneity_completeness_v_measure(y, labels_km), metrics.adjusted_rand_score(y, labels_km), metrics.adjusted_mutual_info_score(y, labels_km)], ['Affinity Propogation',  metrics.calinski_harabaz_score(X, labels_af), metrics.silhouette_score(X, labels_af, metric='euclidean'), metrics.fowlkes_mallows_score(y, labels_af), metrics.homogeneity_completeness_v_measure(y, labels_af), metrics.adjusted_rand_score(y, labels_af), metrics.adjusted_mutual_info_score(y, labels_af)],  ['Mean Shift',  metrics.calinski_harabaz_score(X, labels_mf), metrics.silhouette_score(X, labels_mf, metric='euclidean'), metrics.fowlkes_mallows_score(y, labels_mf), metrics.homogeneity_completeness_v_measure(y, labels_mf), metrics.adjusted_rand_score(y, labels_mf), metrics.adjusted_mutual_info_score(y, labels_mf)], ['DB Scan',  metrics.calinski_harabaz_score(X, labels_mf), metrics.silhouette_score(X, labels_db, metric='euclidean'), metrics.fowlkes_mallows_score(y, labels_db), metrics.homogeneity_completeness_v_measure(y, labels_db), metrics.adjusted_rand_score(y, labels_db), metrics.adjusted_mutual_info_score(y, labels_db)], ['Evidence Accumulation Clustering Ensemble',  metrics.calinski_harabaz_score(X, labels_ea), metrics.silhouette_score(X, labels_ea, metric='euclidean'), metrics.fowlkes_mallows_score(y, labels_ea), metrics.homogeneity_completeness_v_measure(y, labels_ea), metrics.adjusted_rand_score(y, labels_ea), metrics.adjusted_mutual_info_score(y, labels_ea)]])
print t.draw()
