"""
============================================================
MedIntel360
Schema Manager

Loads and manages all semantic metadata required by the AI
engine.

Author : Jainam
============================================================
"""

import json
import re
from pathlib import Path


class SchemaManager:

    # --------------------------------------------------
    # Search Stopwords
    # --------------------------------------------------

    SEARCH_STOPWORDS = {
        "show",
        "give",
        "get",
        "find",
        "list",
        "tell",
        "me",
        "what",
        "which",
        "how",
        "many",
        "much",
        "the",
        "a",
        "an",
        "of",
        "for",
        "to",
        "by",
        "from",
        "in",
        "on",
        "with",
        "and",
        "or",
        "is",
        "are",
        "was",
        "were"}

    def __init__(self):

        # -----------------------------
        # Metadata Root
        # -----------------------------
        self.metadata_path = Path("metadata")
        self.dataset_path = self.metadata_path / "datasets"

        # -----------------------------
        # Global Metadata
        # -----------------------------
        self.version = {}
        self.glossary = {}
        self.synonyms = {}
        self.calculated_metrics = {}
        self.kpis = {}
        self.relationships = {}
        self.business_rules = {}
        self.query_templates = {}
        self.prompt_rules = {}

        # -----------------------------
        # Dataset Metadata
        # -----------------------------
        self.datasets = {}

        # -----------------------------
        # Load Everything
        # -----------------------------
        self.load()

        # --------------------------------------------------
    # Private JSON Loader
    # --------------------------------------------------

    def _load_json(self, filepath: Path):

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

        # --------------------------------------------------
    # Load Global Metadata
    # --------------------------------------------------

    def _load_global_metadata(self):

        self.version = self._load_json(
            self.metadata_path / "version.json"
        )

        self.glossary = self._load_json(
            self.metadata_path / "glossary.json"
        )

        self.synonyms = self._load_json(
            self.metadata_path / "synonym_dictionary.json"
        )

        self.calculated_metrics = self._load_json(
            self.metadata_path / "calculated_metrics.json"
        )

        self.kpis = self._load_json(
            self.metadata_path / "kpis.json"
        )

        self.relationships = self._load_json(
            self.metadata_path / "relationships.json"
        )

        self.business_rules = self._load_json(
            self.metadata_path / "business_rules.json"
        )

        self.query_templates = self._load_json(
            self.metadata_path / "query_templates.json"
        )

        self.prompt_rules = self._load_json(
            self.metadata_path / "prompt_rules.json"
        )

        # --------------------------------------------------
    # Load Dataset Metadata
    # --------------------------------------------------

    def _load_datasets(self):

        self.datasets = {}

        for file in self.dataset_path.glob("*.json"):

            dataset = self._load_json(file)

            dataset_id = dataset["dataset_info"]["id"]

            self.datasets[dataset_id] = dataset

    # --------------------------------------------------
    # Load Metadata
    # --------------------------------------------------

    def load(self):

        self._load_global_metadata()

        self._load_datasets()
    # --------------------------------------------------
    # Dataset Names
    # --------------------------------------------------

    def get_dataset_names(self):

        return list(self.datasets.keys())

    # --------------------------------------------------
    # Get Dataset
    # --------------------------------------------------

    def get_dataset(self, dataset_name):

        if dataset_name not in self.datasets:
            raise ValueError(
                f"Dataset '{dataset_name}' not found."
            )

        return self.datasets[dataset_name]

    # --------------------------------------------------
    # Physical Schema
    # --------------------------------------------------

    def get_physical_schema(self, dataset_name):

        dataset = self.get_dataset(dataset_name)

        return dataset["physical_schema"]

    # --------------------------------------------------
    # Dimensions
    # --------------------------------------------------

    def get_dimensions(self, dataset_name):

        dataset = self.get_dataset(dataset_name)

        return dataset["dimensions"]

    # --------------------------------------------------
    # Metrics
    # --------------------------------------------------

    def get_metrics(self, dataset_name):

        dataset = self.get_dataset(dataset_name)

        return dataset["metrics"]

    # --------------------------------------------------
    # Relationships
    # --------------------------------------------------

    def get_relationships(self):

        return self.relationships

    # --------------------------------------------------
    # Business Rules
    # --------------------------------------------------

    def get_business_rules(self):

        return self.business_rules

    # --------------------------------------------------
    # Synonyms
    # --------------------------------------------------

    def get_synonyms(self):

        return self.synonyms

    # --------------------------------------------------
    # Glossary
    # --------------------------------------------------

    def get_glossary(self):

        return self.glossary

    # --------------------------------------------------
    # Query Templates
    # --------------------------------------------------

    def get_query_templates(self):

        return self.query_templates

    # --------------------------------------------------
    # Column Names
    # --------------------------------------------------

    def get_column_names(self, dataset_name):

        schema = self.get_physical_schema(dataset_name)

        return schema["columns"]

    # --------------------------------------------------
    # Metric Names
    # --------------------------------------------------

    def get_metric_names(self, dataset_name):

        metrics = self.get_metrics(dataset_name)

        return [
            metric["name"]
            for metric in metrics
            ]
    # --------------------------------------------------
    # Dimension Names
    # --------------------------------------------------

    def get_dimension_names(self, dataset_name):

        dimensions = self.get_dimensions(dataset_name)

        return [
            dimension["name"]
            for dimension in dimensions
        ]
    # --------------------------------------------------
    # AI Context
    # --------------------------------------------------

    def get_ai_context(self, dataset_name):

        dataset = self.get_dataset(dataset_name)

        return dataset["ai_context"]

    # --------------------------------------------------
    # Sample Questions
    # --------------------------------------------------

    def get_sample_questions(self, dataset_name):

        dataset = self.get_dataset(dataset_name)

        return dataset["sample_questions"]


    # --------------------------------------------------
    # Search Datasets
    # --------------------------------------------------

    def search_datasets(self, query):

        # --------------------------------------------------
        # Direct description matching
        # --------------------------------------------------

        query_tokens = self._tokenize_query(
            query
        )

        dataset_scores = {}

        for dataset_name, dataset in self.datasets.items():

            info = dataset["dataset_info"]

            searchable_text = " ".join([
                info.get("name", ""),
                info.get("description", "")
            ])

            score = self._calculate_search_score(
                query_tokens,
                searchable_text
            )

            if score > 0:

                dataset_scores[dataset_name] = (
                    dataset_scores.get(dataset_name, 0)
                    + score
                )

        # --------------------------------------------------
        # Vocabulary matching
        # --------------------------------------------------

        matched_terms = self._search_vocabulary(
            query
        )

        vocabulary_datasets = (
            self._datasets_from_glossary_terms(
                matched_terms
            )
        )

        for item in vocabulary_datasets:

            dataset_name = item["dataset"]

            dataset_scores[dataset_name] = (
                dataset_scores.get(dataset_name, 0)
                + item["score"]
            )

        # --------------------------------------------------
        # Build results
        # --------------------------------------------------

        results = []

        for dataset_name, score in dataset_scores.items():

            results.append({
                "dataset": dataset_name,
                "score": score
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results
    
    # --------------------------------------------------
    # Search Dimensions
    # --------------------------------------------------

    def search_dimensions(
        self,
        dataset_name,
        query
    ):

        query_tokens = self._tokenize_query(
            query
        )

        results = []

        for dimension in self.get_dimensions(
            dataset_name
        ):

            searchable_text = " ".join([

                dimension.get(
                    "name",
                    ""
                ),

                dimension.get(
                    "display_name",
                    ""
                ),

                dimension.get(
                    "description",
                    ""
                ),

                " ".join(
                    dimension.get(
                        "aliases",
                        []
                    )
                )
            ])

            score = self._calculate_search_score(
                query_tokens,
                searchable_text
            )

            if score > 0:

                result = dict(dimension)

                result["_search_score"] = score

                results.append(result)

        results.sort(
            key=lambda item: (
                item["_search_score"],
                item.get(
                    "search_weight",
                    0
                )
            ),
            reverse=True
        )

        return results

    # --------------------------------------------------
    # Search Metrics
    # --------------------------------------------------

    def search_metrics(self, dataset_name, query):

        query_tokens = self._tokenize_query(
            query
        )

        results = []

        for metric in self.get_metrics(
            dataset_name
        ):

            searchable_text = " ".join([

                metric.get("name", ""),

                metric.get(
                    "display_name",
                    ""
                ),

                metric.get(
                    "description",
                    ""
                ),

                " ".join(
                    metric.get(
                        "aliases",
                        []
                    )
                )
            ])

            score = self._calculate_search_score(
                query_tokens,
                searchable_text
            )

            if score > 0:

                result = dict(metric)

                result["_search_score"] = score

                results.append(result)

        results.sort(
            key=lambda item: (
                item["_search_score"],
                item.get(
                    "search_weight",
                    0
                )
            ),
            reverse=True
        )

        return results

    # --------------------------------------------------
    # Search Glossary
    # --------------------------------------------------


    def search_glossary(self, query):

        query = query.lower()

        results = {}

        for key, value in self.glossary.items():

            searchable_text = " ".join([
                key,
                str(value)
            ]).lower()

            if query in searchable_text:

                results[key] = value

        return results

    # --------------------------------------------------
    # Tokenize Query
    # --------------------------------------------------



    @classmethod
    def _tokenize_query(cls, text):

        if not isinstance(text, str):

            return set()

        tokens = re.findall(
            r"\b[a-zA-Z0-9_]+\b",
            text.lower()
        )

        return {
            token
            for token in tokens
            if token not in cls.SEARCH_STOPWORDS
        }

    # --------------------------------------------------
    # Calculate Search Score
    # --------------------------------------------------


    @classmethod
    def _calculate_search_score(
        cls,
        query_tokens,
        searchable_text
    ):

        text_tokens = cls._tokenize_query(
            searchable_text
        )

        matched_tokens = (
            query_tokens & text_tokens
        )

        return len(matched_tokens)

    # --------------------------------------------------
    # Search Schema Vocabulary
    # --------------------------------------------------

    def _search_vocabulary(self, query):

        query_tokens = self._tokenize_query(query)

        matched_terms = []

        synonyms_data = self.synonyms.get(
            "synonyms",
            []
        )

        for item in synonyms_data:

            canonical = item.get(
                "canonical_term",
                ""
            )

            aliases = item.get(
                "aliases",
                []
            )

            vocabulary = [canonical] + aliases

            vocabulary_text = " ".join(
                vocabulary
            )

            vocabulary_tokens = self._tokenize_query(
                vocabulary_text
            )

            score = len(
                query_tokens & vocabulary_tokens
            )

            if score > 0:

                matched_terms.append({
                    "canonical_term": canonical,
                    "score": score
                })

        matched_terms.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return matched_terms

    # --------------------------------------------------
    # Get Datasets From Glossary Terms
    # --------------------------------------------------

    def _datasets_from_glossary_terms(
        self,
        matched_terms
    ):

        datasets = {}

        glossary_terms = self.glossary.get(
            "terms",
            []
        )

        for matched in matched_terms:

            canonical = matched[
                "canonical_term"
            ]

            for glossary_item in glossary_terms:

                if glossary_item.get("term", "").lower() != canonical.lower():

                    continue

            for dataset_name in glossary_item.get(
                "datasets",
                []
            ):

                datasets[dataset_name] = (
                    datasets.get(dataset_name, 0)
                    + matched["score"]
                )

        results = []

        for dataset_name, score in datasets.items():

            results.append({
                "dataset": dataset_name,
                "score": score
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results

    # --------------------------------------------------
    # Calculate Dataset Evidence
    # --------------------------------------------------

    def _calculate_dataset_evidence(
        self,
        dataset_name,
        query
    ):

        metrics = self.search_metrics(
            dataset_name,
        query
        )

        dimensions = self.search_dimensions(
            dataset_name,
            query
        )

        metric_score = 0

        dimension_score = 0

        # --------------------------------------------------
        # Metric Evidence
        # --------------------------------------------------

        if metrics:

            metric_score = max(
                (
                    item.get("_search_score", 0)
                    * item.get("search_weight", 0)
                )
                for item in metrics
            )

        # --------------------------------------------------
        # Dimension Evidence
        # --------------------------------------------------

        if dimensions:

            dimension_score = max(
                (
                    item.get("_search_score", 0)
                    * item.get("search_weight", 0)
                )
                for item in dimensions
            )

        # --------------------------------------------------
        # Combined Score
        # --------------------------------------------------

        total_score = (
            metric_score
            + dimension_score
        )

        return {
            "metric_score": metric_score,
            "dimension_score": dimension_score,
            "total_score": total_score
    }

    # --------------------------------------------------
    # Rank Dataset Candidates
    # --------------------------------------------------

    def rank_dataset_candidates(
        self,
        query
    ):

        candidates = self.search_datasets(
            query
        )

        results = []

        for candidate in candidates:

            dataset_name = candidate[
                "dataset"
            ]

            evidence = (
                self._calculate_dataset_evidence(
                    dataset_name,
                    query
                )
            )

            results.append({

                "dataset": dataset_name,

                "base_score": candidate[
                    "score"
                ],

                "metric_score": evidence[
                    "metric_score"
                ],

                "dimension_score": evidence[
                    "dimension_score"
                ],

                "total_score": (
                    evidence["total_score"]
                    + candidate["score"]
                )
            })

        results.sort(
            key=lambda item: item[
                "total_score"
            ],
            reverse=True
        )

        return results