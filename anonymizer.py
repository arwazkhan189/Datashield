import numpy as np
import random
import math
from collections import Counter
from copy import deepcopy

class TransactionDataset:
    def __init__(self, transactions, sensitive_items):
        self.transactions = transactions
        self.sensitive_items = sensitive_items
        self.nonsensitive_items = set()
        self.global_sensitive_dist = self.calculate_sensitive_distribution()

    def calculate_sensitive_distribution(self):
        sensitive_counter = Counter()
        total = 0
        for trans in self.transactions:
            for item in trans:
                if item in self.sensitive_items:
                    sensitive_counter[item] += 1
                    total += 1
                else:
                    self.nonsensitive_items.add(item)
        dist = {item: sensitive_counter[item] / total for item in self.sensitive_items}
        return dist

    def split_sensitive_nonsensitive(self, transaction):
        sensitive = {item for item in transaction if item in self.sensitive_items}
        nonsensitive = {item for item in transaction if item not in self.sensitive_items}
        return sensitive, nonsensitive

class Cluster:
    def __init__(self, transactions):
        self.transactions = transactions
        self.similarity = 0
        self.kl_divergence = 0
        self.fitness = 0

    def calculate_similarity(self, dataset):
        if len(self.transactions) <= 1:
            return 1
        union_items = set()
        intersection_items = None
        for idx in self.transactions:
            trans = dataset.transactions[idx]
            nonsensitive, _ = dataset.split_sensitive_nonsensitive(trans)
            if intersection_items is None:
                intersection_items = nonsensitive.copy()
            else:
                intersection_items &= nonsensitive
            union_items |= nonsensitive
        if not union_items:
            return 0
        similarity = len(intersection_items) / len(union_items)
        self.similarity = similarity
        return similarity

    def calculate_kl_divergence(self, dataset):
        cluster_sensitive_counter = Counter()
        total = 0
        for idx in self.transactions:
            trans = dataset.transactions[idx]
            for item in trans:
                if item in dataset.sensitive_items:
                    cluster_sensitive_counter[item] += 1
                    total += 1
        if total == 0:
            return 0
        cluster_dist = {item: cluster_sensitive_counter[item] / total for item in dataset.sensitive_items}
        kl_div = 0
        for item in dataset.sensitive_items:
            p = max(cluster_dist.get(item, 0), 1e-6)
            q = max(dataset.global_sensitive_dist.get(item, 0), 1e-6)
            kl_div += p * math.log(p / q)
            
        self.kl_divergence = kl_div
        return kl_div

    def calculate_fitness(self, dataset, t, w1=0.5, w2=0.5):
        sim = self.calculate_similarity(dataset)
        kl = self.calculate_kl_divergence(dataset)
        if kl > t:
            self.fitness = w1 * sim + w2 * (1 / (kl - t + 1e-6))
        else:
            self.fitness = sim
        return self.fitness

class GeneticAnonymizer:
    def __init__(self, dataset, k, m, t, generations=50):
        self.dataset = dataset
        self.k = k
        self.m = m
        self.t = t
        self.generations = generations
        self.population = []

    def initialize_population(self):
        indices = list(range(len(self.dataset.transactions)))
        random.shuffle(indices)
        clusters = []
        for i in range(0, len(indices), self.k):
            cluster_indices = indices[i:i+self.k]
            if len(cluster_indices) >= self.k:
                clusters.append(Cluster(cluster_indices))
        self.population = clusters

    def evolve(self):
        for _ in range(self.generations):
            for cluster in self.population:
                cluster.calculate_fitness(self.dataset, self.t)
            self.population.sort(key=lambda c: c.fitness, reverse=True)
            new_population = []
            for i in range(0, len(self.population)-1, 2):
                c1 = self.population[i]
                c2 = self.population[i+1]
                child1, child2 = self.crossover(c1, c2)
                new_population.extend([child1, child2])
            self.population = new_population

    def crossover(self, c1, c2):
        split_point = len(c1.transactions) // 2
        child1_transactions = c1.transactions[:split_point] + c2.transactions[split_point:]
        child2_transactions = c2.transactions[:split_point] + c1.transactions[split_point:]
        return Cluster(child1_transactions), Cluster(child2_transactions)

    def get_final_clusters(self):
        return self.population

def verpart(cluster_transactions, dataset, k, m):
    items_counter = Counter()
    for idx in cluster_transactions:
        nonsensitive, _ = dataset.split_sensitive_nonsensitive(dataset.transactions[idx])
        items_counter.update(nonsensitive)

    term_chunk = {item for item, count in items_counter.items() if count < k}
    remain_items = set(items_counter.keys()) - term_chunk

    record_chunks = []
    while remain_items:
        current_chunk = set()
        for item in list(remain_items):
            test_chunk = current_chunk | {item}
            support = sum(1 for idx in cluster_transactions if test_chunk.issubset(
                dataset.split_sensitive_nonsensitive(dataset.transactions[idx])[0]))
            if support >= k and len(test_chunk) <= m:
                current_chunk.add(item)
        if not current_chunk:
            break
        record_chunks.append(current_chunk)
        remain_items -= current_chunk
        
    print("record_chunks:", record_chunks)
    print("term_chunk:", term_chunk)
    return record_chunks, term_chunk

def anonymize_transactions(transactions, sensitive_items, k, m, t):
    dataset = TransactionDataset(transactions, sensitive_items)
    ga = GeneticAnonymizer(dataset, k, m, t)
    ga.initialize_population()
    ga.evolve()

    final_clusters = ga.get_final_clusters()
    results = []

    for cluster in final_clusters:
        record_chunks, term_chunk = verpart(cluster.transactions, dataset, k, m)
        results.append({
            "record_chunks": [list(chunk) for chunk in record_chunks],
            "term_chunk": list(term_chunk)
        })

    print(f"Clusters formed: {len(final_clusters)}")
    return results