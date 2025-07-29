"""
Semantic service for entity disambiguation, ontology reasoning, and knowledge inference.
"""
import re
import logging
from typing import List, Dict, Any, Tuple, Optional, Set
from collections import defaultdict, Counter
import networkx as nx
from models.database import db
from .vector_service import VectorService

logger = logging.getLogger(__name__)

class SemanticService:
    """Semantic service for knowledge graph reasoning and entity disambiguation."""
    
    def __init__(self, vector_service: VectorService = None):
        """Initialize semantic service."""
        self.vector_service = vector_service or VectorService()
        self.ontology_graph = nx.DiGraph()
        self.entity_hierarchy = {}
        self.disambiguation_rules = {}
        
        # Course category hierarchy
        self.course_hierarchy = {
            '艺术类': ['绘画', '音乐', '舞蹈', '书法', '声乐', '合唱', '素描', '水彩', '油画', '国画', '篆刻', '陶艺'],
            '体育类': ['篮球', '足球', '游泳', '跆拳道', '乒乓球', '羽毛球', '网球', '武术', '击剑', '射箭', '攀岩', '轮滑', '滑冰', '滑雪', '马术', '高尔夫'],
            '技术类': ['编程', 'Python编程', 'C++', 'scratch', 'kitchen', '乐高', '人工智能', '航模'],
            '棋类': ['围棋', '象棋', '国际象棋', '跳棋', '五子棋', '军棋', '飞行棋'],
            '乐器类': ['钢琴', '小提琴', '大提琴', '古筝', '二胡', '笛子', '萨克斯', '吉他'],
            '语言类': ['英语', '日语', '韩语', '法语', '德语'],
            '学科类': ['数学', '科学', '科学实验', '天文']
        }
        
        # Initialize ontology
        self._build_ontology()
    
    def _build_ontology(self):
        """Build ontology graph from course hierarchy."""
        # Add root node
        self.ontology_graph.add_node('COURSE', type='root', level=0)
        
        # Add category nodes and relationships
        for category, courses in self.course_hierarchy.items():
            self.ontology_graph.add_node(category, type='category', level=1)
            self.ontology_graph.add_edge('COURSE', category, relation='has_subcategory')
            
            # Add course nodes
            for course in courses:
                self.ontology_graph.add_node(course, type='course', level=2)
                self.ontology_graph.add_edge(category, course, relation='contains')
                
                # Store hierarchy mapping
                self.entity_hierarchy[course] = {
                    'category': category,
                    'root': 'COURSE',
                    'level': 2
                }
    
    def get_entity_category(self, entity_name: str) -> Optional[str]:
        """Get the category of an entity."""
        return self.entity_hierarchy.get(entity_name, {}).get('category')
    
    def get_related_entities(self, entity_name: str, relation_type: str = None) -> List[str]:
        """Get entities related to the given entity."""
        if entity_name not in self.ontology_graph:
            return []
        
        related = []
        
        if relation_type == 'siblings':
            # Get sibling entities (same category)
            category = self.get_entity_category(entity_name)
            if category:
                related = [node for node in self.ontology_graph.predecessors(category) 
                          if node != entity_name and self.ontology_graph.nodes[node]['type'] == 'course']
        
        elif relation_type == 'parent':
            # Get parent category
            parents = list(self.ontology_graph.predecessors(entity_name))
            related = [p for p in parents if self.ontology_graph.nodes[p]['type'] == 'category']
        
        elif relation_type == 'children':
            # Get child entities
            children = list(self.ontology_graph.successors(entity_name))
            related = [c for c in children if self.ontology_graph.nodes[c]['type'] == 'course']
        
        else:
            # Get all related entities
            related = list(self.ontology_graph.neighbors(entity_name))
        
        return related
    
    def disambiguate_entity(self, text: str, context: str = "", 
                          candidates: List[str] = None) -> Dict[str, Any]:
        """Disambiguate entity based on context and semantic similarity."""
        if not candidates:
            # Find potential candidates using vector similarity
            if self.vector_service.index:
                similar_results = self.vector_service.search(text, k=10, threshold=0.3)
                candidates = [r['text'] for r in similar_results]
            else:
                # Fallback to exact and partial matches
                candidates = self._find_candidate_entities(text)
        
        if not candidates:
            return {'entity': text, 'confidence': 0.0, 'candidates': []}
        
        # Score candidates based on multiple factors
        scored_candidates = []
        
        for candidate in candidates:
            score = self._calculate_disambiguation_score(text, candidate, context)
            scored_candidates.append({
                'entity': candidate,
                'score': score,
                'category': self.get_entity_category(candidate)
            })
        
        # Sort by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        best_match = scored_candidates[0] if scored_candidates else None
        
        return {
            'entity': best_match['entity'] if best_match else text,
            'confidence': best_match['score'] if best_match else 0.0,
            'category': best_match['category'] if best_match else None,
            'candidates': scored_candidates[:5]  # Top 5 candidates
        }
    
    def _find_candidate_entities(self, text: str) -> List[str]:
        """Find candidate entities using string matching."""
        candidates = []
        text_lower = text.lower()
        
        # Check all entities in hierarchy
        for entity in self.entity_hierarchy.keys():
            entity_lower = entity.lower()
            
            # Exact match
            if text_lower == entity_lower:
                candidates.append(entity)
            # Partial match
            elif text_lower in entity_lower or entity_lower in text_lower:
                candidates.append(entity)
        
        return candidates
    
    def _calculate_disambiguation_score(self, text: str, candidate: str, context: str) -> float:
        """Calculate disambiguation score for a candidate entity."""
        score = 0.0
        
        # 1. String similarity
        string_sim = self._string_similarity(text, candidate)
        score += string_sim * 0.4
        
        # 2. Vector similarity (if available)
        if self.vector_service.model:
            try:
                vector_sim = self.vector_service.compute_similarity(text, candidate)
                score += vector_sim * 0.3
            except:
                pass
        
        # 3. Context relevance
        if context:
            context_score = self._calculate_context_relevance(candidate, context)
            score += context_score * 0.2
        
        # 4. Entity frequency/popularity (could be based on usage statistics)
        popularity_score = self._get_entity_popularity(candidate)
        score += popularity_score * 0.1
        
        return min(score, 1.0)
    
    def _string_similarity(self, text1: str, text2: str) -> float:
        """Calculate string similarity using Levenshtein distance."""
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(text1.lower(), text2.lower())
        max_len = max(len(text1), len(text2))
        return 1.0 - (distance / max_len) if max_len > 0 else 0.0
    
    def _calculate_context_relevance(self, entity: str, context: str) -> float:
        """Calculate how relevant an entity is to the given context."""
        if not context:
            return 0.0
        
        # Get related entities
        related_entities = self.get_related_entities(entity, 'siblings')
        category = self.get_entity_category(entity)
        
        relevance_score = 0.0
        context_lower = context.lower()
        
        # Check if category is mentioned in context
        if category and category.lower() in context_lower:
            relevance_score += 0.5
        
        # Check if related entities are mentioned
        for related in related_entities:
            if related.lower() in context_lower:
                relevance_score += 0.1
        
        return min(relevance_score, 1.0)
    
    def _get_entity_popularity(self, entity: str) -> float:
        """Get entity popularity score (placeholder for now)."""
        # This could be based on actual usage statistics from the database
        # For now, return a default score
        return 0.5
    
    def infer_bio_label(self, entity: str, position: str = "B") -> str:
        """Infer BIO label for an entity."""
        category = self.get_entity_category(entity)
        
        if category:
            # Map category to BIO label
            bio_tag = f"{position}-COURSE-{entity}"
        else:
            # Default to generic course label
            bio_tag = f"{position}-COURSE-{entity}"
        
        return bio_tag
    
    def validate_bio_sequence(self, bio_sequence: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Validate BIO sequence and suggest corrections."""
        issues = []
        
        for i, (token, label) in enumerate(bio_sequence):
            # Check for invalid B-I sequences
            if label.startswith('I-') and i > 0:
                prev_label = bio_sequence[i-1][1]
                if not prev_label.startswith('B-') and not prev_label.startswith('I-'):
                    issues.append({
                        'position': i,
                        'issue': 'I-label without preceding B-label',
                        'suggestion': f"Change to B-{label[2:]}"
                    })
                elif prev_label.startswith('B-') or prev_label.startswith('I-'):
                    # Check if entity types match
                    prev_entity = prev_label[2:] if len(prev_label) > 2 else ""
                    curr_entity = label[2:] if len(label) > 2 else ""
                    if prev_entity != curr_entity:
                        issues.append({
                            'position': i,
                            'issue': 'Entity type mismatch in sequence',
                            'suggestion': f"Change to B-{curr_entity} or I-{prev_entity}"
                        })
        
        return issues
    
    def suggest_entity_relations(self, entity1: str, entity2: str) -> List[Dict[str, Any]]:
        """Suggest possible relations between two entities."""
        relations = []
        
        cat1 = self.get_entity_category(entity1)
        cat2 = self.get_entity_category(entity2)
        
        if cat1 == cat2:
            relations.append({
                'relation': 'SIMILAR_TO',
                'confidence': 0.8,
                'reason': 'Same category'
            })
        
        # Check if entities are in the same hierarchy path
        if entity1 in self.ontology_graph and entity2 in self.ontology_graph:
            try:
                path = nx.shortest_path(self.ontology_graph, entity1, entity2)
                if len(path) <= 3:  # Close in hierarchy
                    relations.append({
                        'relation': 'RELATED_TO',
                        'confidence': 0.6,
                        'reason': f'Close in hierarchy (distance: {len(path)-1})'
                    })
            except nx.NetworkXNoPath:
                pass
        
        # Vector similarity (if available)
        if self.vector_service.model:
            try:
                similarity = self.vector_service.compute_similarity(entity1, entity2)
                if similarity > 0.7:
                    relations.append({
                        'relation': 'SEMANTICALLY_SIMILAR',
                        'confidence': similarity,
                        'reason': f'High semantic similarity ({similarity:.2f})'
                    })
            except:
                pass
        
        return relations
    
    def get_ontology_stats(self) -> Dict[str, Any]:
        """Get statistics about the ontology."""
        return {
            'total_nodes': self.ontology_graph.number_of_nodes(),
            'total_edges': self.ontology_graph.number_of_edges(),
            'categories': len(self.course_hierarchy),
            'total_courses': sum(len(courses) for courses in self.course_hierarchy.values()),
            'max_depth': max(self.ontology_graph.nodes[node].get('level', 0) 
                           for node in self.ontology_graph.nodes()),
            'hierarchy_coverage': len(self.entity_hierarchy)
        }
    
    def export_ontology(self, format_type: str = "json") -> Dict[str, Any]:
        """Export ontology in specified format."""
        if format_type == "json":
            return {
                'nodes': [
                    {
                        'id': node,
                        'type': self.ontology_graph.nodes[node].get('type', 'unknown'),
                        'level': self.ontology_graph.nodes[node].get('level', 0)
                    }
                    for node in self.ontology_graph.nodes()
                ],
                'edges': [
                    {
                        'source': edge[0],
                        'target': edge[1],
                        'relation': self.ontology_graph.edges[edge].get('relation', 'unknown')
                    }
                    for edge in self.ontology_graph.edges()
                ],
                'hierarchy': self.course_hierarchy
            }
        else:
            raise ValueError(f"Unsupported format: {format_type}")

