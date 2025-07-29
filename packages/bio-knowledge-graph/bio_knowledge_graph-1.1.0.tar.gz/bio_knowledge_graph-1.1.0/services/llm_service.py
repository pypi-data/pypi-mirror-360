"""
LLM service for intelligent annotation assistance and natural language processing.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import openai
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

logger = logging.getLogger(__name__)

class LLMService:
    """LLM service for intelligent annotation and NLP tasks."""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize LLM service."""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        self.ner_model = None
        self.ner_tokenizer = None
        self.ner_pipeline = None
        
        # BIO标签系统提示词
        self.bio_system_prompt = """
你是一个专业的BIO标注专家，专门处理教育课程相关的实体识别和标注。

BIO标注规则：
- B-COURSE-xxx: 课程实体的开始标记
- I-COURSE-xxx: 课程实体的延续标记
- O: 非课程相关内容

课程类别包括：
- 艺术类：绘画、音乐、舞蹈、书法、声乐等
- 体育类：篮球、足球、游泳、跆拳道等
- 技术类：编程、Python、人工智能、乐高等
- 棋类：围棋、象棋、国际象棋等
- 乐器类：钢琴、小提琴、古筝等
- 语言类：英语、日语、韩语等
- 学科类：数学、科学、科学实验等

请根据上下文准确识别课程实体并进行BIO标注。
"""
    
    def load_ner_model(self, model_name: str = "hfl/chinese-bert-wwm-ext"):
        """Load pre-trained NER model."""
        try:
            self.ner_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.ner_model = AutoModelForTokenClassification.from_pretrained(model_name)
            
            # Create NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model=self.ner_model,
                tokenizer=self.ner_tokenizer,
                aggregation_strategy="simple"
            )
            
            logger.info(f"NER model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
    
    def suggest_bio_annotation(self, text: str, context: str = "") -> Dict[str, Any]:
        """Suggest BIO annotation using LLM."""
        if not self.openai_api_key:
            return self._fallback_annotation(text)
        
        prompt = f"""
请对以下文本进行BIO标注，识别其中的课程相关实体：

文本: {text}
上下文: {context}

请返回JSON格式的结果，包含：
1. tokens: 分词结果
2. labels: 对应的BIO标签
3. entities: 识别出的实体列表
4. confidence: 标注置信度

示例格式：
{{
    "tokens": ["喜", "欢", "学", "习", "钢", "琴"],
    "labels": ["O", "O", "O", "O", "B-COURSE-钢琴", "I-COURSE-钢琴"],
    "entities": [
        {{
            "text": "钢琴",
            "label": "COURSE-钢琴",
            "start": 4,
            "end": 6,
            "confidence": 0.95
        }}
    ],
    "confidence": 0.9
}}
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.bio_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM JSON response")
                return self._fallback_annotation(text)
                
        except Exception as e:
            logger.error(f"LLM annotation failed: {e}")
            return self._fallback_annotation(text)
    
    def _fallback_annotation(self, text: str) -> Dict[str, Any]:
        """Fallback annotation using rule-based approach."""
        # Simple rule-based annotation
        course_keywords = [
            '绘画', '音乐', '舞蹈', '书法', '编程', '钢琴', '小提琴', 
            '篮球', '足球', '游泳', '英语', '数学', '科学'
        ]
        
        tokens = list(text)
        labels = ['O'] * len(tokens)
        entities = []
        
        for keyword in course_keywords:
            start = text.find(keyword)
            if start != -1:
                end = start + len(keyword)
                labels[start] = f'B-COURSE-{keyword}'
                for i in range(start + 1, end):
                    if i < len(labels):
                        labels[i] = f'I-COURSE-{keyword}'
                
                entities.append({
                    'text': keyword,
                    'label': f'COURSE-{keyword}',
                    'start': start,
                    'end': end,
                    'confidence': 0.8
                })
        
        return {
            'tokens': tokens,
            'labels': labels,
            'entities': entities,
            'confidence': 0.7
        }
    
    def batch_annotate(self, texts: List[str], context: str = "") -> List[Dict[str, Any]]:
        """Batch annotate multiple texts."""
        results = []
        for text in texts:
            result = self.suggest_bio_annotation(text, context)
            results.append(result)
        
        return results
    
    def validate_annotation(self, tokens: List[str], labels: List[str]) -> Dict[str, Any]:
        """Validate BIO annotation sequence."""
        issues = []
        suggestions = []
        
        for i, (token, label) in enumerate(zip(tokens, labels)):
            # Check for invalid I- without B-
            if label.startswith('I-') and i > 0:
                prev_label = labels[i-1]
                if not prev_label.startswith('B-') and not prev_label.startswith('I-'):
                    issues.append({
                        'position': i,
                        'token': token,
                        'label': label,
                        'issue': 'I-label without preceding B-label',
                        'severity': 'error'
                    })
                    suggestions.append({
                        'position': i,
                        'original': label,
                        'suggested': f"B-{label[2:]}",
                        'reason': 'Convert I- to B- at sequence start'
                    })
                
                # Check entity consistency
                elif prev_label.startswith(('B-', 'I-')):
                    prev_entity = prev_label[2:] if len(prev_label) > 2 else ""
                    curr_entity = label[2:] if len(label) > 2 else ""
                    if prev_entity != curr_entity:
                        issues.append({
                            'position': i,
                            'token': token,
                            'label': label,
                            'issue': 'Entity type mismatch in sequence',
                            'severity': 'warning'
                        })
        
        return {
            'is_valid': len([issue for issue in issues if issue['severity'] == 'error']) == 0,
            'issues': issues,
            'suggestions': suggestions,
            'total_entities': len([label for label in labels if label.startswith('B-')])
        }
    
    def extract_entities_with_ner(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using pre-trained NER model."""
        if not self.ner_pipeline:
            logger.warning("NER model not loaded")
            return []
        
        try:
            entities = self.ner_pipeline(text)
            
            # Convert to our format
            formatted_entities = []
            for entity in entities:
                formatted_entities.append({
                    'text': entity['word'],
                    'label': entity['entity_group'],
                    'start': entity['start'],
                    'end': entity['end'],
                    'confidence': entity['score']
                })
            
            return formatted_entities
            
        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            return []
    
    def generate_annotation_explanation(self, text: str, annotation: Dict[str, Any]) -> str:
        """Generate explanation for annotation decisions."""
        if not self.openai_api_key:
            return "标注基于规则匹配和语义分析"
        
        entities = annotation.get('entities', [])
        entity_list = [f"{e['text']}({e['label']})" for e in entities]
        
        prompt = f"""
请解释以下BIO标注的决策过程：

原文本: {text}
识别的实体: {', '.join(entity_list)}

请简要说明：
1. 为什么这些词被识别为课程实体
2. 标注的依据是什么
3. 是否有其他可能的标注方式

请用中文回答，保持简洁明了。
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个BIO标注专家，善于解释标注决策。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return "无法生成标注解释"
    
    def suggest_similar_annotations(self, text: str, k: int = 5) -> List[Dict[str, Any]]:
        """Suggest similar annotation examples."""
        # This would typically query a database of existing annotations
        # For now, return placeholder suggestions
        
        suggestions = [
            {
                'text': '我喜欢学习钢琴和小提琴',
                'annotation': {
                    'entities': [
                        {'text': '钢琴', 'label': 'COURSE-钢琴'},
                        {'text': '小提琴', 'label': 'COURSE-小提琴'}
                    ]
                },
                'similarity': 0.85
            },
            {
                'text': '他擅长绘画和书法',
                'annotation': {
                    'entities': [
                        {'text': '绘画', 'label': 'COURSE-绘画'},
                        {'text': '书法', 'label': 'COURSE-书法'}
                    ]
                },
                'similarity': 0.78
            }
        ]
        
        return suggestions[:k]
    
    def improve_annotation_with_context(self, text: str, initial_annotation: Dict[str, Any], 
                                      context: str) -> Dict[str, Any]:
        """Improve annotation using additional context."""
        if not self.openai_api_key:
            return initial_annotation
        
        prompt = f"""
请基于额外的上下文信息改进以下BIO标注：

原文本: {text}
当前标注: {json.dumps(initial_annotation, ensure_ascii=False)}
上下文: {context}

请考虑上下文信息，优化标注结果，特别注意：
1. 是否有遗漏的课程实体
2. 是否有误标的实体
3. 实体边界是否准确

返回改进后的JSON格式标注结果。
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.bio_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content
            
            try:
                improved_annotation = json.loads(result_text)
                return improved_annotation
            except json.JSONDecodeError:
                logger.warning("Failed to parse improved annotation")
                return initial_annotation
                
        except Exception as e:
            logger.error(f"Failed to improve annotation: {e}")
            return initial_annotation
    
    def get_annotation_confidence(self, text: str, annotation: Dict[str, Any]) -> float:
        """Calculate confidence score for annotation."""
        entities = annotation.get('entities', [])
        
        if not entities:
            return 0.0
        
        # Calculate average entity confidence
        total_confidence = sum(entity.get('confidence', 0.5) for entity in entities)
        avg_confidence = total_confidence / len(entities)
        
        # Adjust based on text length and entity coverage
        text_length = len(text)
        entity_coverage = sum(len(entity['text']) for entity in entities) / text_length
        
        # Final confidence score
        confidence = avg_confidence * (0.7 + 0.3 * entity_coverage)
        
        return min(confidence, 1.0)

