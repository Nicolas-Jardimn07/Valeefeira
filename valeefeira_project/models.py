from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'produtor' or 'comprador'
    cpf = db.Column(db.String(11), nullable=False)
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)
    
    # Profile picture
    profile_image_data = db.Column(db.LargeBinary)  # Store image as binary data
    profile_image_mimetype = db.Column(db.String(100))  # Store MIME type
    
    # Subscription fields
    subscription_plan = db.Column(db.String(20), default='free')  # free, basic, premium
    subscription_expires = db.Column(db.DateTime)
    featured_products_limit = db.Column(db.Integer, default=0)
    
    # Relationship with products
    products = db.relationship('Product', backref='seller', lazy=True, cascade='all, delete-orphan')
    
    # Relationship with chats
    sent_chats = db.relationship('Chat', foreign_keys='Chat.sender_id', backref='sender', lazy=True)
    received_chats = db.relationship('Chat', foreign_keys='Chat.receiver_id', backref='receiver', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_subscription_active(self):
        """Check if user has an active subscription"""
        if self.subscription_plan == 'free':
            return False
        return self.subscription_expires and self.subscription_expires > datetime.utcnow()
    
    def get_plan_benefits(self):
        """Get benefits for current subscription plan"""
        benefits = {
            'free': {
                'featured_products': 0,
                'priority_listing': False,
                'analytics': False,
                'badge': None
            },
            'basic': {
                'featured_products': 3,
                'priority_listing': True,
                'analytics': True,
                'badge': 'Produtor Verificado'
            },
            'premium': {
                'featured_products': 10,
                'priority_listing': True,
                'analytics': True,
                'badge': 'Produtor Premium'
            }
        }
        return benefits.get(self.subscription_plan, benefits['free'])
    
    def can_feature_product(self):
        """Check if user can feature more products"""
        if not self.is_subscription_active():
            return False
        benefits = self.get_plan_benefits()
        featured_count = Product.query.filter_by(seller_id=self.id, is_featured=True).count()
        return featured_count < benefits['featured_products']
    
    def get_average_rating(self):
        """Get average rating for seller"""
        if not self.reviews_received:
            return 0
        total_rating = sum([review.rating for review in self.reviews_received])
        return round(total_rating / len(self.reviews_received), 1)
    
    def get_rating_count(self):
        """Get total number of reviews received"""
        return len(self.reviews_received)
    
    def get_star_display(self):
        """Return star display for seller rating"""
        avg_rating = self.get_average_rating()
        full_stars = int(avg_rating)
        half_star = 1 if (avg_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        result = '★' * full_stars
        if half_star:
            result += '☆'
        result += '☆' * empty_stars
        return result
    
    def generate_reset_token(self):
        """Generate a secure reset token"""
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify if reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear reset token after successful password reset"""
        self.reset_token = None
        self.reset_token_expires = None

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, unidade, caixa, etc.
    quantity_available = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(255))
    image_data = db.Column(db.LargeBinary)  # Store image as binary data
    image_mimetype = db.Column(db.String(100))  # Store MIME type
    is_organic = db.Column(db.Boolean, default=False)
    harvest_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Foreign key to User
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def get_average_rating(self):
        """Get average rating for product"""
        if not self.reviews:
            return 0
        total_rating = sum([review.rating for review in self.reviews])
        return round(total_rating / len(self.reviews), 1)
    
    def get_rating_count(self):
        """Get total number of reviews for product"""
        return len(self.reviews)
    
    def get_star_display(self):
        """Return star display for product rating"""
        avg_rating = self.get_average_rating()
        full_stars = int(avg_rating)
        half_star = 1 if (avg_rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        result = '★' * full_stars
        if half_star:
            result += '☆'
        result += '☆' * empty_stars
        return result
    
    def can_be_reviewed_by(self, user_id):
        """Check if user can review this product"""
        if not user_id:
            return False
        # User cannot review their own product
        if self.seller_id == user_id:
            return False
        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            product_id=self.id, 
            reviewer_id=user_id
        ).first()
        return existing_review is None
    
    def is_favorited_by(self, user_id):
        """Check if product is favorited by user"""
        if not user_id:
            return False
        return Favorite.query.filter_by(user_id=user_id, product_id=self.id).first() is not None
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Chat {self.id}: {self.message[:50]}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified_purchase = db.Column(db.Boolean, default=False)
    
    # Relationships
    product = db.relationship('Product', backref='reviews')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_given')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='reviews_received')
    
    def __repr__(self):
        return f'<Review {self.id}: {self.rating} stars for Product {self.product_id}>'
    
    def get_star_display(self):
        """Return star display for template"""
        full_stars = self.rating
        empty_stars = 5 - self.rating
        return '★' * full_stars + '☆' * empty_stars


class Favorite(db.Model):
    """User favorites for products"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='favorites')
    product = db.relationship('Product', backref='favorited_by')
    
    # Unique constraint to prevent duplicate favorites
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_favorite'),)
    
    def __repr__(self):
        return f'<Favorite {self.user_id}:{self.product_id}>'
