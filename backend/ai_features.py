# ==========================================
# 🤖 ADVANCED AI FEATURES MODULE
# ==========================================

import random
import string
from datetime import datetime, timedelta

# ==========================================
# AI-POWERED TITLE GENERATION
# ==========================================
class AITitleGenerator:
    def __init__(self):
        self.adjectives = [
            'Premium', 'Excellent', 'Brand New', 'High Quality', 'Professional',
            'Rare', 'Authentic', 'Original', 'Genuine', 'Modern', 'Classic',
            'Elegant', 'Stylish', 'Durable', 'Reliable', 'Practical'
        ]
        self.conditions = [
            'Condition', 'State', 'Quality', 'Status', 'Form'
        ]

    def generate_variations(self, base_title, count=5):
        """Generate AI variations of a title."""
        variations = [base_title]
        
        for _ in range(count - 1):
            adj = random.choice(self.adjectives)
            variation = f"{adj} {base_title}"
            variations.append(variation)
        
        return variations

    def optimize_for_seo(self, title):
        """Optimize title for search."""
        words = title.split()
        # Move important words to front
        if len(words) > 1:
            return f"{words[-1]} {' '.join(words[:-1])}"
        return title

# ==========================================
# AI DESCRIPTION GENERATOR
# ==========================================
class AIDescriptionGenerator:
    def __init__(self):
        self.templates = [
            "Brand new {product}. Never used. Perfect condition. Fast shipping. Secure packaging.",
            "High quality {product}. Excellent {condition}. Great price! Must see. Buy now!",
            "Authentic {product}. Certified. Great deal. Limited availability. Don't miss out!",
            "Professional grade {product}. Well maintained. {condition} condition. Negotiable price.",
            "Premium {product}. Recently acquired. Like new. Perfect gift. Free delivery available.",
        ]

    def generate(self, product_name, condition="New"):
        """Generate AI description."""
        template = random.choice(self.templates)
        return template.format(product=product_name, condition=condition)

# ==========================================
# AI TAG SUGGESTION
# ==========================================
class AITagSuggester:
    def __init__(self):
        self.category_tags = {
            'Electronics': ['smartphone', 'laptop', 'tablet', 'gaming', 'audio', 'camera', 'tech'],
            'Furniture': ['modern', 'vintage', 'office', 'bedroom', 'living room', 'design'],
            'Clothing': ['fashion', 'designer', 'casual', 'formal', 'vintage', 'brand new'],
            'Books': ['reading', 'education', 'vintage', 'rare', 'collectible', 'fiction'],
            'Sports': ['fitness', 'outdoor', 'gym', 'exercise', 'training', 'recreation'],
            'Appliances': ['kitchen', 'home', 'new', 'energy efficient', 'sale'],
        }

    def suggest_tags(self, category, count=5):
        """Suggest tags for category."""
        tags = self.category_tags.get(category, [])
        selected = random.sample(tags, min(count, len(tags)))
        return selected

# ==========================================
# AI PRICE OPTIMIZER
# ==========================================
class AIPriceOptimizer:
    @staticmethod
    def suggest_price_variation(base_price, variation_percent=10):
        """Suggest slight price variations for A/B testing."""
        variation = (base_price * variation_percent) / 100
        prices = [
            base_price,
            base_price + variation,
            base_price - variation,
            base_price * 1.15,
            base_price * 0.85,
        ]
        return [round(p, 2) for p in prices]

    @staticmethod
    def round_price_psychologically(price):
        """Round price for psychological effect."""
        # .99 prices are more appealing
        return int(price) + 0.99

# ==========================================
# AI LISTING TIMING OPTIMIZER
# ==========================================
class AIListingTimingOptimizer:
    @staticmethod
    def get_best_posting_times():
        """Get AI-optimized best times to post listings."""
        now = datetime.now()
        best_times = [
            now + timedelta(hours=h) 
            for h in [6, 10, 14, 18, 20]  # Peak hours
        ]
        return best_times

    @staticmethod
    def get_renewal_schedule(days_interval=3):
        """Get schedule for renewing listings."""
        renewals = []
        for i in range(10):
            renewal_time = datetime.now() + timedelta(days=days_interval * (i + 1))
            renewals.append(renewal_time)
        return renewals

# ==========================================
# AI BEHAVIOR ANALYZER
# ==========================================
class AIBehaviorAnalyzer:
    def __init__(self):
        self.listing_performance = {}

    def analyze_listing_success(self, listing_id, views=0, clicks=0, sales=0):
        """Analyze listing performance."""
        return {
            'listing_id': listing_id,
            'ctr': (clicks / max(views, 1)) * 100,  # Click-through rate
            'conversion': (sales / max(clicks, 1)) * 100,  # Conversion rate
            'performance_score': (sales * 3 + clicks * 1 + views * 0.1) / 100,
        }

    def get_recommendations(self, listing_data):
        """Get AI recommendations for improvement."""
        recommendations = []
        
        if len(listing_data.get('title', '')) < 20:
            recommendations.append("⚠️ Title too short. Add more keywords.")
        
        if len(listing_data.get('description', '')) < 50:
            recommendations.append("⚠️ Description too short. Add more details.")
        
        if not listing_data.get('images'):
            recommendations.append("❌ No images. Add at least 3 images.")
        elif len(listing_data.get('images', [])) < 3:
            recommendations.append("⚠️ Add more images (minimum 3 recommended).")
        
        if not listing_data.get('tags'):
            recommendations.append("⚠️ Add tags for better visibility.")
        
        return recommendations

# ==========================================
# AI FRAUD DETECTION
# ==========================================
class AIFraudDetector:
    @staticmethod
    def is_suspicious_activity(attempt_count, time_window_minutes=60):
        """Detect suspicious activity patterns."""
        # More than 20 listings in 1 hour = suspicious
        return attempt_count > 20

    @staticmethod
    def get_safe_rate_limit():
        """Get safe rate limit to avoid ban."""
        return {
            'listings_per_hour': 5,
            'listings_per_day': 50,
            'min_delay_between_listings': 30,  # seconds
        }

# ==========================================
# INITIALIZE ALL AI MODULES
# ==========================================
title_generator = AITitleGenerator()
description_generator = AIDescriptionGenerator()
tag_suggester = AITagSuggester()
price_optimizer = AIPriceOptimizer()
timing_optimizer = AIListingTimingOptimizer()
behavior_analyzer = AIBehaviorAnalyzer()
fraud_detector = AIFraudDetector()
