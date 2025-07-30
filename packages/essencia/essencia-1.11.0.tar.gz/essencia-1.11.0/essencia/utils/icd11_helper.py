"""
ICD-11 Helper - Utilities for working with the optimized ICD-11 database
"""
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import unicodedata
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Severity levels for ICD-11 codes"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VARIES = "varies"


@dataclass
class ICD11Code:
    """Represents an ICD-11 diagnostic code"""
    code: str
    title: str
    category: str
    group: str
    severity: str
    keywords: List[str]
    description: str
    specifiers: List[str]
    symptom_links: List[int]
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def matches_severity(self, severity: Severity) -> bool:
        """Check if code matches severity level"""
        return self.severity == severity.value


class ICD11DB:
    """Optimized ICD-11 database with fast search and clinical utilities"""
    
    def __init__(self, json_path: str = None):
        if json_path is None:
            json_path = Path(__file__).parent.parent.parent / "storage/data/json/icd11_optimized.json"
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Direct access to flat codes for O(1) lookup
        self.codes = self.data['codes_flat']
        
        # Load symptoms database for integration
        self._load_symptoms_db()
    
    def _load_symptoms_db(self):
        """Load symptoms database for cross-reference"""
        try:
            from .symptoms_helper import SymptomsDB
            self.symptoms_db = SymptomsDB()
        except:
            self.symptoms_db = None
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for search (remove accents, lowercase)"""
        text = unicodedata.normalize('NFD', text.lower())
        return ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    def get_code(self, code: str) -> Optional[ICD11Code]:
        """Get ICD-11 code by exact code"""
        if code in self.codes:
            data = self.codes[code]
            return ICD11Code(**data)
        return None
    
    def search(self, query: str, limit: int = 10) -> List[ICD11Code]:
        """Search ICD-11 codes by text matching"""
        normalized_query = self.normalize_text(query)
        words = normalized_query.split()
        
        results = []
        scores = {}
        
        # Check search index first
        search_index = self.data['search_index']
        for word in words:
            if word in search_index:
                for code_prefix in search_index[word]:
                    # Find all codes that start with this prefix
                    for code, data in self.codes.items():
                        if code.startswith(code_prefix):
                            scores[code] = scores.get(code, 0) + 10
                            if code not in [r.code for r in results]:
                                results.append(ICD11Code(**data))
        
        # Search in titles and keywords
        for code, data in self.codes.items():
            if code in [r.code for r in results]:
                continue
                
            score = 0
            normalized_title = self.normalize_text(data['title'])
            normalized_keywords = [self.normalize_text(k) for k in data['keywords']]
            
            for word in words:
                if word in normalized_title:
                    score += 8
                elif any(word in part for part in normalized_title.split()):
                    score += 4
                
                for keyword in normalized_keywords:
                    if word == keyword:
                        score += 6
                    elif word in keyword:
                        score += 2
            
            if score > 0:
                scores[code] = scores.get(code, 0) + score
                results.append(ICD11Code(**data))
        
        # Sort by score
        results.sort(key=lambda c: scores.get(c.code, 0), reverse=True)
        
        return results[:limit]
    
    def get_by_category(self, category_code: str) -> List[ICD11Code]:
        """Get all codes in a category"""
        if category_code in self.data['categories']:
            subcodes = self.data['categories'][category_code]['subcodes']
            return [self.get_code(code) for code in subcodes if code in self.codes]
        return []
    
    def get_by_group(self, group_id: str) -> List[ICD11Code]:
        """Get all codes in a category group"""
        results = []
        for code, data in self.codes.items():
            if data['group'] == group_id:
                results.append(ICD11Code(**data))
        return results
    
    def get_by_severity(self, severity: Severity) -> List[ICD11Code]:
        """Get codes by severity level"""
        severity_codes = self.data['severity_map'].get(severity.value, [])
        results = []
        
        for code in severity_codes:
            # Handle both specific codes and category prefixes
            if code in self.codes:
                results.append(self.get_code(code))
            else:
                # It's a category prefix
                for full_code, data in self.codes.items():
                    if full_code.startswith(code) and data['severity'] == severity.value:
                        results.append(ICD11Code(**data))
        
        return results
    
    def get_differential_diagnosis(self, code: str) -> List[ICD11Code]:
        """Get differential diagnosis codes for a given code"""
        # Extract base code (without subtype)
        base_code = code.split('.')[0]
        
        if base_code in self.data['differential_diagnosis']:
            diff_codes = self.data['differential_diagnosis'][base_code]
            results = []
            
            for diff_code in diff_codes:
                if diff_code in self.codes:
                    results.append(self.get_code(diff_code))
                else:
                    # It's a category, get first code
                    for full_code, data in self.codes.items():
                        if full_code.startswith(diff_code):
                            results.append(ICD11Code(**data))
                            break
            
            return results
        return []
    
    def get_comorbidities(self, code: str) -> List[ICD11Code]:
        """Get common comorbidities for a given code"""
        base_code = code.split('.')[0]
        
        if base_code in self.data['comorbidity_patterns']:
            comorbid_codes = self.data['comorbidity_patterns'][base_code]
            results = []
            
            for comorbid_code in comorbid_codes:
                if comorbid_code in self.codes:
                    results.append(self.get_code(comorbid_code))
                else:
                    # It's a category, get first code
                    for full_code, data in self.codes.items():
                        if full_code.startswith(comorbid_code):
                            results.append(ICD11Code(**data))
                            break
            
            return results
        return []
    
    def get_clinical_pathway(self, pathway_name: str) -> List[ICD11Code]:
        """Get codes in a clinical pathway"""
        if pathway_name in self.data['clinical_pathways']:
            pathway_codes = self.data['clinical_pathways'][pathway_name]
            results = []
            
            for pathway_code in pathway_codes:
                if pathway_code in self.codes:
                    results.append(self.get_code(pathway_code))
                else:
                    # It's a category, get all codes in it
                    for full_code, data in self.codes.items():
                        if full_code.startswith(pathway_code):
                            results.append(ICD11Code(**data))
            
            return results
        return []
    
    def get_symptoms_for_code(self, code: str) -> List[Dict[str, Any]]:
        """Get symptoms associated with an ICD-11 code"""
        if not self.symptoms_db:
            return []
        
        icd_code = self.get_code(code)
        if not icd_code:
            return []
        
        symptoms = []
        for symptom_id in icd_code.symptom_links:
            symptom = self.symptoms_db.get_by_id(symptom_id)
            if symptom:
                symptoms.append(symptom)
        
        return symptoms
    
    def suggest_codes_from_symptoms(self, symptom_ids: List[int], limit: int = 5) -> List[Tuple[ICD11Code, int]]:
        """Suggest ICD-11 codes based on symptoms"""
        code_scores = {}
        
        for code, data in self.codes.items():
            matching_symptoms = set(data.get('symptom_links', [])) & set(symptom_ids)
            if matching_symptoms:
                score = len(matching_symptoms)
                code_scores[code] = score
        
        # Sort by score
        sorted_codes = sorted(code_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for code, score in sorted_codes[:limit]:
            icd_code = self.get_code(code)
            if icd_code:
                results.append((icd_code, score))
        
        return results
    
    def get_hierarchy(self, code: str) -> Dict[str, Any]:
        """Get hierarchical information for a code"""
        icd_code = self.get_code(code)
        if not icd_code:
            return {}
        
        # Get category info
        category = self.data['categories'].get(icd_code.category, {})
        
        # Get group info
        group = self.data['category_groups'].get(icd_code.group, {})
        
        return {
            'code': icd_code,
            'category': category,
            'group': group,
            'siblings': self.get_by_category(icd_code.category)
        }
    
    def export_for_ui(self, group_id: str = None) -> List[Dict[str, Any]]:
        """Export codes in a format suitable for UI display"""
        if group_id:
            codes = self.get_by_group(group_id)
        else:
            codes = [ICD11Code(**data) for data in self.codes.values()]
        
        groups = self.data['category_groups']
        
        return [
            {
                'code': c.code,
                'title': c.title,
                'group': groups.get(c.group, {}).get('name', c.group),
                'group_color': groups.get(c.group, {}).get('color', '#666'),
                'group_icon': groups.get(c.group, {}).get('icon', '📋'),
                'severity': c.severity,
                'description': c.description[:100] + '...' if len(c.description) > 100 else c.description
            }
            for c in codes
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_codes': len(self.codes),
            'total_categories': len(self.data['categories']),
            'total_groups': len(self.data['category_groups']),
            'codes_by_group': {
                group: len(self.get_by_group(group))
                for group in self.data['category_groups']
            },
            'codes_by_severity': {
                severity.value: len(self.get_by_severity(severity))
                for severity in Severity
            }
        }


# Integration with existing models
def find_icd11_codes_for_diagnosis(diagnosis_text: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Find ICD-11 codes that match a diagnosis text"""
    db = ICD11DB()
    codes = db.search(diagnosis_text, limit=limit)
    
    return [
        {
            'code': c.code,
            'title': c.title,
            'description': c.description,
            'confidence': 0.8 if diagnosis_text.lower() in c.title.lower() else 0.6
        }
        for c in codes
    ]


def validate_icd11_code(code: str) -> bool:
    """Validate if a code exists in the ICD-11 database"""
    db = ICD11DB()
    return db.get_code(code) is not None


def get_icd11_hierarchy_display(code: str) -> str:
    """Get a formatted hierarchy display for a code"""
    db = ICD11DB()
    hierarchy = db.get_hierarchy(code)
    
    if not hierarchy:
        return ""
    
    group = hierarchy['group']
    category = hierarchy['category']
    code_obj = hierarchy['code']
    
    return f"{group.get('icon', '')} {group.get('name', '')} > {category.get('title', '')} > {code_obj.title}"


# Demo functions
def demo_search():
    """Demonstrate search functionality"""
    db = ICD11DB()
    
    # Search for depression
    print("=== Searching for 'depressão' ===")
    results = db.search("depressão", limit=5)
    for code in results:
        print(f"{code.code} - {code.title}")
        print(f"  Severity: {code.severity}")
        print(f"  Keywords: {', '.join(code.keywords[:3])}")
    
    # Search for anxiety
    print("\n=== Searching for 'ansiedade pânico' ===")
    results = db.search("ansiedade pânico", limit=5)
    for code in results:
        print(f"{code.code} - {code.title}")


def demo_clinical_features():
    """Demonstrate clinical features"""
    db = ICD11DB()
    
    # Get differential diagnosis
    print("=== Differential diagnosis for Major Depression (6A70) ===")
    diff_codes = db.get_differential_diagnosis("6A70.1")
    for code in diff_codes:
        print(f"  - {code.code}: {code.title}")
    
    # Get comorbidities
    print("\n=== Common comorbidities for Borderline (6D14) ===")
    comorbid_codes = db.get_comorbidities("6D14.0")
    for code in comorbid_codes:
        print(f"  - {code.code}: {code.title}")
    
    # Get clinical pathway
    print("\n=== Depression spectrum disorders ===")
    pathway_codes = db.get_clinical_pathway("depression_spectrum")
    for code in pathway_codes[:5]:
        print(f"  - {code.code}: {code.title}")


def demo_symptom_integration():
    """Demonstrate symptom integration"""
    db = ICD11DB()
    
    # Get symptoms for a code
    print("=== Symptoms for PTSD (6B40.0) ===")
    symptoms = db.get_symptoms_for_code("6B40.0")
    for symptom in symptoms:
        print(f"  - {symptom['text']}")
    
    # Suggest codes from symptoms
    print("\n=== Suggested codes for symptoms [1, 4, 6, 7] ===")
    symptom_ids = [1, 4, 6, 7]  # Depression, hopelessness, anhedonia, suicidal ideation
    suggestions = db.suggest_codes_from_symptoms(symptom_ids)
    for code, score in suggestions:
        print(f"  - {code.code}: {code.title} (score: {score})")


def demo_ui_export():
    """Demonstrate UI export functionality"""
    db = ICD11DB()
    
    print("=== UI Export for Anxiety Disorders ===")
    ui_data = db.export_for_ui("anxiety")
    for item in ui_data[:3]:
        print(f"{item['group_icon']} {item['code']} - {item['title']}")
        print(f"   Group: {item['group']} (color: {item['group_color']})")
        print(f"   {item['description']}")


if __name__ == "__main__":
    print("=== ICD-11 Database Demo ===\n")
    
    demo_search()
    print("\n" + "="*50 + "\n")
    
    demo_clinical_features()
    print("\n" + "="*50 + "\n")
    
    demo_symptom_integration()
    print("\n" + "="*50 + "\n")
    
    demo_ui_export()
    
    # Show statistics
    db = ICD11DB()
    stats = db.get_statistics()
    print("\n=== Database Statistics ===")
    print(f"Total codes: {stats['total_codes']}")
    print(f"Total categories: {stats['total_categories']}")
    print(f"Total groups: {stats['total_groups']}")
    print("\nCodes by group:")
    for group, count in stats['codes_by_group'].items():
        print(f"  - {group}: {count}")