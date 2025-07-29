"""
Comprehensive annotation service integrating multiple annotation methods with local multilingual-e5-base model.
"""
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
import numpy as np

from .vector_service import VectorService
from .semantic_service import SemanticService
from .llm_service import LLMService
from config import get_config

logger = logging.getLogger(__name__)

class AnnotationService:
    """Comprehensive annotation service for BIO tagging."""
    
    def __init__(self):
        """Initialize annotation service with local model configuration."""
        self.config = get_config()
        
        # Initialize services with local model configuration
        self.vector_service = VectorService(
            model_path=self.config.LOCAL_MODEL_PATH,
            dimension=self.config.VECTOR_DIMENSION
        )
        self.semantic_service = SemanticService()
        self.llm_service = LLMService()
        
        # Load vector model
        self._load_vector_model()
        
        logger.info("AnnotationService initialized with local multilingual-e5-base model")
    
    def _load_vector_model(self):
        """Load the local vector model."""
        try:
            success = self.vector_service.load_model()
            if success:
                logger.info("Local multilingual-e5-base model loaded successfully")
            else:
                logger.warning("Failed to load local model, some features may not work")
        except Exception as e:
            logger.error(f"Error loading vector model: {e}")
    
    def annotate_text(self, text: str, context: str = "", use_llm: bool = True, use_vector: bool = True) -> Dict[str, Any]:
        """
        Annotate text using multiple methods with local model.
        
        Args:
            text: Input text to annotate
            context: Additional context for annotation
            use_llm: Whether to use LLM for annotation
            use_vector: Whether to use vector similarity for annotation
            
        Returns:
            Dict: Annotation results with entities and confidence
        """
        try:
            logger.info(f"Annotating text: {text[:50]}...")
            
            # Extract potential entities
            potential_entities = self._extract_potential_entities(text)
            
            # Collect annotations from different methods
            all_entities = []
            methods_used = []
            
            # 1. Semantic rule-based annotation
            semantic_entities = self._semantic_annotation(text, potential_entities)
            all_entities.extend(semantic_entities)
            methods_used.append("semantic")
            
            # 2. Vector similarity annotation (using local model)
            if use_vector and self.vector_service.model is not None:
                vector_entities = self._vector_annotation(text, potential_entities, context)
                all_entities.extend(vector_entities)
                methods_used.append("vector")
            
            # 3. LLM annotation (optional)
            if use_llm and self.llm_service.client is not None:
                llm_entities = self._llm_annotation(text, context)
                all_entities.extend(llm_entities)
                methods_used.append("llm")
            
            # Merge and deduplicate entities
            merged_entities = self._merge_entities(all_entities)
            
            # Generate BIO sequence
            tokens, labels = self._entities_to_bio_sequence(text, merged_entities)
            
            # Calculate overall confidence
            result = {
                "text": text,
                "tokens": tokens,
                "labels": labels,
                "entities": merged_entities,
                "methods_used": methods_used,
                "potential_entities": potential_entities
            }
            
            result["confidence"] = self._calculate_overall_confidence(result)
            
            logger.info(f"Annotation completed. Found {len(merged_entities)} entities with confidence {result['confidence']:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Annotation failed: {e}")
            return {
                "text": text,
                "tokens": list(text),
                "labels": ["O"] * len(text),
                "entities": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def batch_annotate(self, texts: List[str], context: str = "", use_llm: bool = True, use_vector: bool = True) -> List[Dict[str, Any]]:
        """
        Batch annotate multiple texts.
        
        Args:
            texts: List of texts to annotate
            context: Additional context for annotation
            use_llm: Whether to use LLM for annotation
            use_vector: Whether to use vector similarity for annotation
            
        Returns:
            List[Dict]: List of annotation results
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Processing text {i+1}/{len(texts)}")
            result = self.annotate_text(text, context, use_llm, use_vector)
            results.append(result)
        
        return results
    
    def _extract_potential_entities(self, text: str) -> List[str]:
        """
        Extract potential course entities from text using patterns.
        
        Args:
            text: Input text
            
        Returns:
            List[str]: List of potential entities
        """
        entities = []
        
        # Common course-related patterns
        patterns = [
            r'(?:学习|学|练习|练|上|教|教授|培训)([^，。！？\s]{1,6})',
            r'([^，。！？\s]{1,6})(?:课程|课|班|培训|教学|学习)',
            r'(?:喜欢|爱好|兴趣|擅长|会|能)([^，。！？\s]{1,6})',
            r'([^，。！？\s]{1,6})(?:技能|能力|水平|基础)',
            r'(?:参加|报名|选择)([^，。！？\s]{1,6})(?:课程|班|培训)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        # Remove duplicates and filter
        entities = list(set(entities))
        entities = [e for e in entities if len(e) >= 2 and len(e) <= 6]
        
        return entities
    
    def _semantic_annotation(self, text: str, potential_entities: List[str]) -> List[Dict[str, Any]]:
        """
        Perform semantic rule-based annotation.
        
        Args:
            text: Input text
            potential_entities: List of potential entities
            
        Returns:
            List[Dict]: Semantic annotation results
        """
        entities = []
        
        for entity in potential_entities:
            if entity in text:
                # Get entity category and BIO label
                category = self.semantic_service.get_entity_category(entity)
                if category:
                    bio_label = self.semantic_service.infer_bio_label(entity, "B")
                    
                    # Calculate confidence based on semantic features
                    confidence = self._calculate_semantic_confidence(entity, text, category)
                    
                    entities.append({
                        "text": entity,
                        "label": bio_label,
                        "confidence": confidence,
                        "source": "semantic",
                        "category": category
                    })
        
        return entities
    
    def _vector_annotation(self, text: str, potential_entities: List[str], context: str = "") -> List[Dict[str, Any]]:
        """
        Perform vector similarity-based annotation using local model.
        
        Args:
            text: Input text
            potential_entities: List of potential entities
            context: Additional context
            
        Returns:
            List[Dict]: Vector annotation results
        """
        entities = []
        
        try:
            # Combine text and context for better embedding
            full_text = f"{context} {text}".strip() if context else text
            
            for entity in potential_entities:
                if entity in text:
                    # Find similar entities using vector search
                    similar_entities = self.vector_service.find_similar(entity, k=5)
                    
                    if similar_entities:
                        # Calculate confidence based on similarity scores
                        max_similarity = max([result["score"] for result in similar_entities])
                        confidence = min(max_similarity, 0.95)  # Cap at 0.95
                        
                        # Infer BIO label based on similar entities
                        bio_label = self.semantic_service.infer_bio_label(entity, "B")
                        
                        entities.append({
                            "text": entity,
                            "label": bio_label,
                            "confidence": confidence,
                            "source": "vector",
                            "similar_entities": similar_entities[:3]  # Top 3 similar
                        })
            
        except Exception as e:
            logger.error(f"Vector annotation failed: {e}")
        
        return entities
    
    def _llm_annotation(self, text: str, context: str = "") -> List[Dict[str, Any]]:
        """
        Perform LLM-based annotation.
        
        Args:
            text: Input text
            context: Additional context
            
        Returns:
            List[Dict]: LLM annotation results
        """
        try:
            # Use LLM service for annotation
            llm_result = self.llm_service.annotate_text(text, context)
            
            entities = []
            if "entities" in llm_result:
                for entity_info in llm_result["entities"]:
                    entities.append({
                        "text": entity_info.get("text", ""),
                        "label": entity_info.get("label", "O"),
                        "confidence": entity_info.get("confidence", 0.5),
                        "source": "llm",
                        "explanation": entity_info.get("explanation", "")
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"LLM annotation failed: {e}")
            return []
    
    def _merge_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge entities from different sources and remove duplicates.
        
        Args:
            entities: List of entities from different sources
            
        Returns:
            List[Dict]: Merged and deduplicated entities
        """
        # Group entities by text
        entity_groups = defaultdict(list)
        for entity in entities:
            entity_groups[entity["text"]].append(entity)
        
        merged_entities = []
        for text, group in entity_groups.items():
            if len(group) == 1:
                merged_entities.append(group[0])
            else:
                # Merge multiple annotations for the same entity
                merged_entity = self._merge_entity_group(group)
                merged_entities.append(merged_entity)
        
        # Sort by confidence
        merged_entities.sort(key=lambda x: x["confidence"], reverse=True)
        
        return merged_entities
    
    def _merge_entity_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple annotations for the same entity.
        
        Args:
            group: List of annotations for the same entity
            
        Returns:
            Dict: Merged entity annotation
        """
        # Use the annotation with highest confidence as base
        base_entity = max(group, key=lambda x: x["confidence"])
        
        # Calculate weighted confidence
        total_confidence = sum([e["confidence"] for e in group])
        avg_confidence = total_confidence / len(group)
        
        # Boost confidence if multiple methods agree
        confidence_boost = min(0.1 * (len(group) - 1), 0.2)
        final_confidence = min(avg_confidence + confidence_boost, 1.0)
        
        # Merge sources
        sources = [e["source"] for e in group]
        
        merged_entity = base_entity.copy()
        merged_entity.update({
            "confidence": final_confidence,
            "sources": sources,
            "agreement_count": len(group)
        })
        
        return merged_entity
    
    def _calculate_semantic_confidence(self, entity: str, text: str, category: str) -> float:
        """
        Calculate confidence for semantic annotation.
        
        Args:
            entity: Entity text
            text: Full text
            category: Entity category
            
        Returns:
            float: Confidence score
        """
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on entity length
        if len(entity) >= 2:
            confidence += 0.1
        if len(entity) >= 3:
            confidence += 0.1
        
        # Boost confidence if entity appears in known patterns
        patterns = [
            f"学习{entity}", f"{entity}课程", f"喜欢{entity}",
            f"练习{entity}", f"{entity}培训", f"学{entity}"
        ]
        
        for pattern in patterns:
            if pattern in text:
                confidence += 0.15
                break
        
        # Boost confidence based on category
        if category:
            confidence += 0.2
        
        return min(confidence, 0.9)  # Cap at 0.9 for semantic
    
    def _entities_to_bio_sequence(self, text: str, entities: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """
        Convert entities to BIO sequence.
        
        Args:
            text: Input text
            entities: List of entities
            
        Returns:
            Tuple[List[str], List[str]]: Tokens and BIO labels
        """
        tokens = list(text)
        labels = ["O"] * len(tokens)
        
        # Sort entities by position in text
        entity_positions = []
        for entity in entities:
            entity_text = entity["text"]
            start_pos = text.find(entity_text)
            if start_pos >= 0:
                entity_positions.append({
                    "start": start_pos,
                    "end": start_pos + len(entity_text),
                    "label": entity["label"],
                    "text": entity_text
                })
        
        # Sort by start position
        entity_positions.sort(key=lambda x: x["start"])
        
        # Apply BIO labels
        for entity_pos in entity_positions:
            start, end = entity_pos["start"], entity_pos["end"]
            base_label = entity_pos["label"]
            
            # Extract the label type (e.g., "COURSE-钢琴" from "B-COURSE-钢琴")
            if base_label.startswith("B-"):
                label_type = base_label[2:]  # Remove "B-"
                
                # Set B- label for first character
                if start < len(labels):
                    labels[start] = f"B-{label_type}"
                
                # Set I- labels for remaining characters
                for i in range(start + 1, min(end, len(labels))):
                    labels[i] = f"I-{label_type}"
        
        return tokens, labels
    
    def _calculate_overall_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate overall confidence for the annotation result.
        
        Args:
            result: Annotation result
            
        Returns:
            float: Overall confidence score
        """
        entities = result.get("entities", [])
        methods_used = result.get("methods_used", [])
        
        if not entities:
            return 0.0
        
        # Average entity confidence
        avg_confidence = sum([e["confidence"] for e in entities]) / len(entities)
        
        # Boost confidence based on number of methods used
        method_boost = min(0.1 * (len(methods_used) - 1), 0.2)
        
        # Boost confidence based on entity agreement
        agreement_boost = 0.0
        for entity in entities:
            if entity.get("agreement_count", 1) > 1:
                agreement_boost += 0.05
        
        agreement_boost = min(agreement_boost, 0.15)
        
        final_confidence = min(avg_confidence + method_boost + agreement_boost, 1.0)
        
        return final_confidence
    
    def get_annotation_suggestions(self, text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Get annotation suggestions for text using local model.
        
        Args:
            text: Input text
            k: Number of suggestions to return
            
        Returns:
            List[Dict]: Annotation suggestions
        """
        try:
            suggestions = []
            
            # Extract potential entities
            potential_entities = self._extract_potential_entities(text)
            
            for entity in potential_entities[:k]:
                # Get similar entities using vector search
                similar_entities = self.vector_service.find_similar(entity, k=3)
                
                # Get semantic information
                category = self.semantic_service.get_entity_category(entity)
                bio_label = self.semantic_service.infer_bio_label(entity, "B")
                
                suggestion = {
                    "entity": entity,
                    "suggested_label": bio_label,
                    "category": category,
                    "similar_entities": similar_entities,
                    "confidence": self._calculate_semantic_confidence(entity, text, category)
                }
                
                suggestions.append(suggestion)
            
            # Sort by confidence
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get annotation suggestions: {e}")
            return []
    
    def validate_annotation(self, tokens: List[str], labels: List[str]) -> Dict[str, Any]:
        """
        Validate BIO annotation sequence.
        
        Args:
            tokens: List of tokens
            labels: List of BIO labels
            
        Returns:
            Dict: Validation results
        """
        return self.semantic_service.validate_bio_sequence(list(zip(tokens, labels)))
    
    def explain_annotation(self, text: str, annotation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain annotation decisions.
        
        Args:
            text: Input text
            annotation: Annotation result
            
        Returns:
            Dict: Explanation of annotation decisions
        """
        explanations = []
        
        entities = annotation.get("entities", [])
        methods_used = annotation.get("methods_used", [])
        
        for entity in entities:
            explanation = {
                "entity": entity["text"],
                "label": entity["label"],
                "confidence": entity["confidence"],
                "source": entity["source"],
                "reasoning": []
            }
            
            # Add reasoning based on source
            if entity["source"] == "semantic":
                explanation["reasoning"].append("基于语义规则识别")
                if "category" in entity:
                    explanation["reasoning"].append(f"属于{entity['category']}类别")
            
            elif entity["source"] == "vector":
                explanation["reasoning"].append("基于向量相似度识别")
                if "similar_entities" in entity:
                    similar_texts = [e.get("metadata", {}).get("text", "") for e in entity["similar_entities"]]
                    explanation["reasoning"].append(f"与以下实体相似: {', '.join(similar_texts[:2])}")
            
            elif entity["source"] == "llm":
                explanation["reasoning"].append("基于大语言模型识别")
                if "explanation" in entity:
                    explanation["reasoning"].append(entity["explanation"])
            
            explanations.append(explanation)
        
        return {
            "text": text,
            "methods_used": methods_used,
            "entity_explanations": explanations,
            "overall_confidence": annotation.get("confidence", 0.0)
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get annotation service statistics.
        
        Returns:
            Dict: Service statistics
        """
        stats = {
            "vector_service": self.vector_service.get_stats(),
            "semantic_service": self.semantic_service.get_stats() if hasattr(self.semantic_service, 'get_stats') else {},
            "llm_service": self.llm_service.get_stats() if hasattr(self.llm_service, 'get_stats') else {},
            "local_model_path": self.config.LOCAL_MODEL_PATH,
            "vector_dimension": self.config.VECTOR_DIMENSION
        }
        
        return stats

