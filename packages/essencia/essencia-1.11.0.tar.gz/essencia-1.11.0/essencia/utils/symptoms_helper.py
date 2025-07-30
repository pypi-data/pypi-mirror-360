"""
Symptoms Helper - Utilities for working with the optimized symptoms database
"""
import json
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import unicodedata


class SymptomsDB:
    """Optimized symptoms database with fast search and filtering capabilities"""
    
    def __init__(self, json_path: str = None):
        if json_path is None:
            json_path = Path(__file__).parent.parent.parent / "storage/data/json/symptoms_optimized.json"
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self._build_indexes()
    
    def _build_indexes(self):
        """Build runtime indexes for faster lookups"""
        # Build symptom by ID index
        self.symptoms_by_id = {s['id']: s for s in self.data['symptoms']}
        
        # Build symptoms by category index
        self.symptoms_by_category = {}
        for symptom in self.data['symptoms']:
            category = symptom['category']
            if category not in self.symptoms_by_category:
                self.symptoms_by_category[category] = []
            self.symptoms_by_category[category].append(symptom)
        
        # Build ICD-11 reverse index
        self.symptoms_by_icd11 = {}
        for symptom in self.data['symptoms']:
            for code in symptom.get('icd11', []):
                if code not in self.symptoms_by_icd11:
                    self.symptoms_by_icd11[code] = []
                self.symptoms_by_icd11[code].append(symptom['id'])
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for search (remove accents, lowercase)"""
        text = unicodedata.normalize('NFD', text.lower())
        return ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search symptoms by text matching"""
        normalized_query = self.normalize_text(query)
        words = normalized_query.split()
        
        results = []
        scores = {}
        
        # Search in symptom text and keywords
        for symptom in self.data['symptoms']:
            score = 0
            normalized_text = self.normalize_text(symptom['text'])
            normalized_keywords = [self.normalize_text(k) for k in symptom.get('keywords', [])]
            
            # Check each word in query
            for word in words:
                # Exact match in symptom text
                if word in normalized_text:
                    score += 10
                
                # Partial match in symptom text
                elif any(word in part for part in normalized_text.split()):
                    score += 5
                
                # Match in keywords
                for keyword in normalized_keywords:
                    if word == keyword:
                        score += 8
                    elif word in keyword:
                        score += 3
            
            if score > 0:
                scores[symptom['id']] = score
                results.append(symptom)
        
        # Sort by score
        results.sort(key=lambda s: scores.get(s['id'], 0), reverse=True)
        
        return results[:limit]
    
    def get_by_id(self, symptom_id: int) -> Optional[Dict[str, Any]]:
        """Get symptom by ID"""
        return self.symptoms_by_id.get(symptom_id)
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all symptoms in a category"""
        return self.symptoms_by_category.get(category, [])
    
    def get_by_icd11(self, icd11_code: str) -> List[Dict[str, Any]]:
        """Get symptoms associated with an ICD-11 code"""
        symptom_ids = self.symptoms_by_icd11.get(icd11_code, [])
        return [self.symptoms_by_id[sid] for sid in symptom_ids]
    
    def get_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get symptoms by severity level"""
        return [s for s in self.data['symptoms'] if s.get('severity') == severity]
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all category information"""
        return self.data['categories']
    
    def get_related_symptoms(self, symptom_id: int) -> List[Dict[str, Any]]:
        """Get symptoms related to the given symptom"""
        symptom = self.get_by_id(symptom_id)
        if not symptom:
            return []
        
        related = set()
        
        # Same category symptoms
        category_symptoms = self.get_by_category(symptom['category'])
        for s in category_symptoms:
            if s['id'] != symptom_id:
                related.add(s['id'])
        
        # Symptoms with overlapping ICD-11 codes
        for code in symptom.get('icd11', []):
            for sid in self.symptoms_by_icd11.get(code, []):
                if sid != symptom_id:
                    related.add(sid)
        
        # Get symptom clusters
        for cluster_name, cluster_ids in self.data['relationships']['symptom_clusters'].items():
            if symptom_id in cluster_ids:
                related.update(sid for sid in cluster_ids if sid != symptom_id)
        
        return [self.get_by_id(sid) for sid in related]
    
    def get_symptom_cluster(self, symptom_id: int) -> Optional[str]:
        """Get the cluster name for a symptom"""
        for cluster_name, cluster_ids in self.data['relationships']['symptom_clusters'].items():
            if symptom_id in cluster_ids:
                return cluster_name
        return None
    
    def get_comorbid_categories(self, category: str) -> List[str]:
        """Get categories commonly comorbid with the given category"""
        return self.data['relationships']['comorbidities'].get(category, [])
    
    def suggest_symptoms(self, existing_symptoms: List[int], limit: int = 5) -> List[Dict[str, Any]]:
        """Suggest additional symptoms based on existing ones"""
        suggestions = {}
        
        # Analyze existing symptoms
        categories = {}
        clusters = set()
        
        for symptom_id in existing_symptoms:
            symptom = self.get_by_id(symptom_id)
            if symptom:
                # Count categories
                cat = symptom['category']
                categories[cat] = categories.get(cat, 0) + 1
                
                # Check clusters
                cluster = self.get_symptom_cluster(symptom_id)
                if cluster:
                    clusters.add(cluster)
        
        # Get symptoms from same clusters
        for cluster_name in clusters:
            cluster_ids = self.data['relationships']['symptom_clusters'][cluster_name]
            for sid in cluster_ids:
                if sid not in existing_symptoms:
                    suggestions[sid] = suggestions.get(sid, 0) + 3
        
        # Get symptoms from dominant category
        if categories:
            dominant_category = max(categories, key=categories.get)
            for symptom in self.get_by_category(dominant_category):
                if symptom['id'] not in existing_symptoms:
                    suggestions[symptom['id']] = suggestions.get(symptom['id'], 0) + 2
            
            # Get symptoms from comorbid categories
            for comorbid_cat in self.get_comorbid_categories(dominant_category):
                for symptom in self.get_by_category(comorbid_cat):
                    if symptom['id'] not in existing_symptoms:
                        suggestions[symptom['id']] = suggestions.get(symptom['id'], 0) + 1
        
        # Sort by score and return top suggestions
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return [self.get_by_id(sid) for sid, _ in sorted_suggestions[:limit]]
    
    def export_for_ui(self, category: str = None) -> List[Dict[str, Any]]:
        """Export symptoms in a format suitable for UI display"""
        if category:
            symptoms = self.get_by_category(category)
        else:
            symptoms = self.data['symptoms']
        
        return [
            {
                'id': s['id'],
                'text': s['text'],
                'category': self.data['categories'][s['category']]['name'],
                'severity': s.get('severity', 'unknown'),
                'icd11_codes': s.get('icd11', [])
            }
            for s in symptoms
        ]


# Example usage functions
def demo_search():
    """Demonstrate search functionality"""
    db = SymptomsDB()
    
    # Search for depression-related symptoms
    results = db.search("depressão tristeza", limit=5)
    print("Search results for 'depressão tristeza':")
    for r in results:
        print(f"  - {r['text']} (ID: {r['id']})")
    
    # Search for anxiety symptoms
    results = db.search("ansiedade pânico", limit=5)
    print("\nSearch results for 'ansiedade pânico':")
    for r in results:
        print(f"  - {r['text']} (ID: {r['id']})")


def demo_relationships():
    """Demonstrate relationship features"""
    db = SymptomsDB()
    
    # Get related symptoms for "Ideação suicida"
    symptom_id = 7  # Ideação suicida
    related = db.get_related_symptoms(symptom_id)
    print(f"Symptoms related to 'Ideação suicida':")
    for r in related[:5]:
        print(f"  - {r['text']} (Category: {r['category']})")
    
    # Get symptom cluster
    cluster = db.get_symptom_cluster(symptom_id)
    print(f"\nSymptom cluster: {cluster}")
    
    # Get comorbid categories
    comorbid = db.get_comorbid_categories('mood_affective')
    print(f"\nCategories commonly comorbid with mood/affective disorders: {comorbid}")


def demo_suggestions():
    """Demonstrate symptom suggestion feature"""
    db = SymptomsDB()
    
    # Patient presents with these symptoms
    existing = [1, 4, 6, 12]  # Depression, hopelessness, anhedonia, chronic fatigue
    suggestions = db.suggest_symptoms(existing)
    
    print("Based on existing symptoms:")
    for sid in existing:
        s = db.get_by_id(sid)
        print(f"  - {s['text']}")
    
    print("\nSuggested additional symptoms to assess:")
    for s in suggestions:
        print(f"  - {s['text']} (Category: {s['category']})")


if __name__ == "__main__":
    print("=== Symptoms Database Demo ===\n")
    
    demo_search()
    print("\n" + "="*50 + "\n")
    
    demo_relationships()
    print("\n" + "="*50 + "\n")
    
    demo_suggestions()