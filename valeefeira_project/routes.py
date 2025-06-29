import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, abort, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from app import app, db
from models import User, Product, Chat, Review, Favorite
from forms import RegistrationForm, LoginForm, ProductForm, SearchForm, ChatForm, ReviewForm, ForgotPasswordForm, ResetPasswordForm, EditProfileForm
from utils import get_cities, save_uploaded_image, send_reset_email

@app.route('/image/<int:product_id>')
def serve_image(product_id):
    """Serve product image from database"""
    product = Product.query.get_or_404(product_id)
    
    if not product.image_data:
        abort(404)
    
    # Create response with image data
    response = make_response(product.image_data)
    response.headers['Content-Type'] = product.image_mimetype or 'image/jpeg'
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year cache
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    
    return response

@app.route('/profile_image/<int:user_id>')
def serve_profile_image(user_id):
    """Serve user profile image from database"""
    user = User.query.get_or_404(user_id)
    
    if not user.profile_image_data:
        abort(404)
    
    # Create response with image data
    response = make_response(user.profile_image_data)
    response.headers['Content-Type'] = user.profile_image_mimetype or 'image/jpeg'
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year cache
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    
    return response

@app.route('/')
def index():
    """Home page showing featured products"""
    search_form = SearchForm()
    search_form.city.choices = [('', 'Todas as cidades')] + [(city, city) for city in get_cities()]
    
    # Get featured products first, then recent products
    featured_products = Product.query.filter_by(is_active=True, is_featured=True).order_by(Product.created_at.desc()).limit(3).all()
    recent_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(6).all()
    
    # Get search parameters
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    
    # Build query
    products_query = Product.query.filter_by(is_active=True)
    
    if query:
        products_query = products_query.filter(Product.name.contains(query))
    if category:
        products_query = products_query.filter_by(category=category)
    if city:
        products_query = products_query.join(User).filter(User.city == city)
    
    products = products_query.order_by(Product.created_at.desc()).all()
    
    return render_template('index.html', 
                         recent_products=recent_products, 
                         featured_products=featured_products,
                         products=products,
                         search_form=search_form,
                         query=query,
                         category=category,
                         city=city)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    form.city.choices = [(city, city) for city in get_cities()]
    
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado. Faça login ou use outro email.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data,
            cpf=form.cpf.data,
            phone=form.phone.data,
            city=form.city.data,
            description=form.description.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
        flash('Email ou senha inválidos.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.user_type == 'produtor':
        # Show producer's products
        products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()
        return render_template('dashboard.html', products=products)
    else:
        # Show recent products for buyers
        recent_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(10).all()
        return render_template('dashboard.html', recent_products=recent_products)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product (producers only)"""
    if current_user.user_type != 'produtor':
        flash('Apenas produtores podem adicionar produtos.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ProductForm()
    if form.validate_on_submit():
        # Handle image upload
        image_data = None
        image_mimetype = None
        image_filename = None
        if form.image.data:
            image_result = save_uploaded_image(form.image.data)
            if image_result:
                image_data = image_result['data']
                image_mimetype = image_result['mimetype']
                image_filename = image_result['filename']
        
        # Create new product
        product = Product(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            price=form.price.data,
            unit=form.unit.data,
            quantity_available=form.quantity_available.data,
            image_filename=image_filename,
            image_data=image_data,
            image_mimetype=image_mimetype,
            is_organic=form.is_organic.data,
            harvest_date=form.harvest_date.data,
            seller_id=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_product.html', form=form)

@app.route('/products')
def products():
    """List all products"""
    search_form = SearchForm()
    search_form.city.choices = [('', 'Todas as cidades')] + [(city, city) for city in get_cities()]
    
    # Get search parameters
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    
    # Build query
    products_query = Product.query.filter_by(is_active=True)
    
    if query:
        products_query = products_query.filter(Product.name.contains(query))
    if category:
        products_query = products_query.filter_by(category=category)
    if city:
        products_query = products_query.join(User).filter(User.city == city)
    
    products = products_query.order_by(Product.created_at.desc()).all()
    
    return render_template('products.html', 
                         products=products,
                         search_form=search_form,
                         query=query,
                         category=category,
                         city=city)

@app.route('/product/<int:id>')
def product_detail(id):
    """Product detail page"""
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    """User profile page"""
    user = User.query.get_or_404(user_id)
    
    if user.user_type == 'produtor':
        products = Product.query.filter_by(seller_id=user.id, is_active=True).order_by(Product.created_at.desc()).all()
        return render_template('profile.html', user=user, products=products)
    else:
        return render_template('profile.html', user=user)

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """Edit product (owner only)"""
    product = Product.query.get_or_404(id)
    
    if product.seller_id != current_user.id:
        flash('Você não tem permissão para editar este produto.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        # Handle image deletion if requested
        delete_image = request.form.get('delete_image')
        if delete_image and product.image_data:
            product.image_filename = None
            product.image_data = None
            product.image_mimetype = None
        
        # Handle new image upload
        elif form.image.data:
            image_result = save_uploaded_image(form.image.data)
            if image_result:
                product.image_filename = image_result['filename']
                product.image_data = image_result['data']
                product.image_mimetype = image_result['mimetype']
        
        # Update product
        product.name = form.name.data
        product.description = form.description.data
        product.category = form.category.data
        product.price = form.price.data
        product.unit = form.unit.data
        product.quantity_available = form.quantity_available.data
        product.is_organic = form.is_organic.data
        product.harvest_date = form.harvest_date.data
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_product.html', form=form, product=product)

@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    """Delete product (owner only)"""
    product = Product.query.get_or_404(id)
    
    if product.seller_id != current_user.id:
        flash('Você não tem permissão para excluir este produto.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Image data will be deleted automatically with the product record
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    form = EditProfileForm(original_username=current_user.username, original_email=current_user.email)
    
    if form.validate_on_submit():
        try:
            # Update basic profile data
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.phone = form.phone.data
            current_user.city = form.city.data
            current_user.description = form.description.data
            
            # Handle profile image upload
            if form.profile_image.data:
                image_data, mimetype = save_uploaded_image(form.profile_image.data)
                current_user.profile_image_data = image_data
                current_user.profile_image_mimetype = mimetype
            
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('profile', user_id=current_user.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar perfil. Tente novamente.', 'danger')
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.city.data = current_user.city
        form.description.data = current_user.description
    
    return render_template('edit_profile.html', form=form)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.route('/chat/<int:product_id>/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def chat(product_id, other_user_id):
    """Chat page between two specific users about a product"""
    product = Product.query.get_or_404(product_id)
    other_user = User.query.get_or_404(other_user_id)
    
    # Get chat history between current user and the other user for this product
    chats = Chat.query.filter(
        Chat.product_id == product_id,
        ((Chat.sender_id == current_user.id) & (Chat.receiver_id == other_user_id)) |
        ((Chat.sender_id == other_user_id) & (Chat.receiver_id == current_user.id))
    ).order_by(Chat.created_at.asc()).all()
    
    # Mark received messages as read
    Chat.query.filter(
        Chat.product_id == product_id,
        Chat.sender_id == other_user_id,
        Chat.receiver_id == current_user.id,
        Chat.is_read == False
    ).update({'is_read': True})
    db.session.commit()
    
    form = ChatForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            chat_message = Chat(
                product_id=product_id,
                sender_id=current_user.id,
                receiver_id=other_user_id,
                message=form.message.data
            )
            db.session.add(chat_message)
            db.session.commit()
            flash('Mensagem enviada!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao enviar mensagem. Tente novamente.', 'error')
        
        return redirect(url_for('chat', product_id=product_id, other_user_id=other_user_id))
    
    return render_template('chat.html', product=product, chats=chats, form=form, other_user=other_user)

@app.route('/my_chats')
@login_required
def my_chats():
    """Show all chats for current user grouped by conversation partner"""
    # Get all chats where user is involved
    user_chats = Chat.query.filter(
        (Chat.sender_id == current_user.id) | (Chat.receiver_id == current_user.id)
    ).order_by(Chat.created_at.desc()).all()
    
    # Group by product + other user combination
    chat_groups = {}
    for chat in user_chats:
        # Determine the other user in the conversation
        other_user_id = chat.sender_id if chat.sender_id != current_user.id else chat.receiver_id
        key = f"{chat.product_id}_{other_user_id}"
        
        if key not in chat_groups:
            # Get product and other user details
            product = Product.query.get(chat.product_id)
            other_user = User.query.get(other_user_id)
            
            chat_groups[key] = {
                'product': product,
                'other_user': other_user,
                'latest_chat': chat,
                'unread_count': 0
            }
        
        # Count unread messages received by current user
        if not chat.is_read and chat.receiver_id == current_user.id:
            chat_groups[key]['unread_count'] += 1
    
    return render_template('my_chats.html', chat_groups=chat_groups.values())

@app.route('/subscription_plans')
@login_required
def subscription_plans():
    """Show subscription plans page"""
    if current_user.user_type != 'produtor':
        flash('Apenas produtores podem acessar os planos de assinatura.', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('subscription_plans.html')

@app.route('/create_checkout_session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a checkout session with payment method selection"""
    if current_user.user_type != 'produtor':
        flash('Apenas produtores podem assinar planos.', 'error')
        return redirect(url_for('dashboard'))
    
    plan = request.form.get('plan')
    payment_method = request.form.get('payment_method', 'pix')
    
    if plan not in ['basic', 'premium']:
        flash('Plano inválido.', 'error')
        return redirect(url_for('subscription_plans'))
    
    # Redirect based on payment method
    if payment_method == 'pix':
        return redirect(url_for('pix_payment', plan=plan))
    else:
        return render_template('payment_simulation.html', plan=plan)

@app.route('/pix_payment/<plan>')
@login_required
def pix_payment(plan):
    """Show PIX payment page"""
    if current_user.user_type != 'produtor':
        flash('Apenas produtores podem assinar planos.', 'error')
        return redirect(url_for('dashboard'))
    
    if plan not in ['basic', 'premium']:
        flash('Plano inválido.', 'error')
        return redirect(url_for('subscription_plans'))
    
    # PIX payment details
    plan_details = {
        'basic': {'name': 'Básico', 'price': 19.00},
        'premium': {'name': 'Premium', 'price': 39.00}
    }
    
    # Generate simulated PIX code for demo
    import uuid
    pix_code = f"00020126580014br.gov.bcb.pix0136{str(uuid.uuid4())[:32]}5204000053039865802BR5925Vale e feira Marketplace6009Sao Paulo62070503***6304"
    
    return render_template('pix_payment.html', plan=plan, plan_details=plan_details[plan], pix_code=pix_code)

@app.route('/confirm_pix_payment', methods=['POST'])
@login_required
def confirm_pix_payment():
    """Confirm PIX payment (simulated)"""
    if current_user.user_type != 'produtor':
        flash('Apenas produtores podem assinar planos.', 'error')
        return redirect(url_for('dashboard'))
    
    plan = request.form.get('plan')
    if plan not in ['basic', 'premium']:
        flash('Plano inválido.', 'error')
        return redirect(url_for('subscription_plans'))
    
    # Simulate successful PIX payment
    try:
        from datetime import datetime, timedelta
        
        current_user.subscription_plan = plan
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        
        if plan == 'basic':
            current_user.featured_products_limit = 3
        elif plan == 'premium':
            current_user.featured_products_limit = 10
        
        db.session.commit()
        
        flash(f'Pagamento PIX confirmado! Plano {plan.title()} ativado com sucesso.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao processar pagamento. Tente novamente.', 'error')
        return redirect(url_for('subscription_plans'))

@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    """Process simulated payment"""
    if current_user.user_type != 'produtor':
        flash('Apenas produtores podem assinar planos.', 'error')
        return redirect(url_for('dashboard'))
    
    plan = request.form.get('plan')
    card_number = request.form.get('card_number', '').replace(' ', '')
    
    # Simulate payment validation
    if len(card_number) != 16 or not card_number.isdigit():
        flash('Número do cartão inválido. Use 16 dígitos.', 'error')
        return render_template('payment_simulation.html', plan=plan)
    
    # Simulate successful payment
    if card_number.startswith('4111'):  # Test card number
        # Update user subscription
        current_user.subscription_plan = plan
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        
        # Set featured products limit based on plan
        if plan == 'basic':
            current_user.featured_products_limit = 3
        elif plan == 'premium':
            current_user.featured_products_limit = 10
        
        db.session.commit()
        plan_name = 'BÁSICO' if plan == 'basic' else 'PREMIUM'
        flash(f'Parabéns! Seu plano {plan_name} foi ativado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Pagamento recusado. Use o cartão de teste: 4111 1111 1111 1111', 'error')
        return render_template('payment_simulation.html', plan=plan)

@app.route('/feature_product/<int:product_id>')
@login_required
def feature_product(product_id):
    """Feature a product (for subscribers only)"""
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        flash('Você só pode destacar seus próprios produtos.', 'error')
        return redirect(url_for('dashboard'))
    
    if not current_user.is_subscription_active():
        flash('Você precisa de um plano ativo para destacar produtos.', 'warning')
        return redirect(url_for('subscription_plans'))
    
    if not current_user.can_feature_product():
        benefits = current_user.get_plan_benefits()
        flash(f'Você já atingiu o limite de {benefits["featured_products"]} produtos em destaque do seu plano.', 'warning')
        return redirect(url_for('dashboard'))
    
    product.is_featured = True
    db.session.commit()
    flash(f'Produto "{product.name}" foi colocado em destaque!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/unfeature_product/<int:product_id>')
@login_required
def unfeature_product(product_id):
    """Remove feature from product"""
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        flash('Você só pode gerenciar seus próprios produtos.', 'error')
        return redirect(url_for('dashboard'))
    
    product.is_featured = False
    db.session.commit()
    flash(f'Produto "{product.name}" foi removido do destaque.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    """Add review for a product"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user can review this product
    if not product.can_be_reviewed_by(current_user.id):
        flash('Você não pode avaliar este produto.', 'error')
        return redirect(url_for('product_detail', id=product_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        try:
            review = Review(
                product_id=product_id,
                reviewer_id=current_user.id,
                seller_id=product.seller_id,
                rating=int(form.rating.data),
                title=form.title.data,
                comment=form.comment.data
            )
            db.session.add(review)
            db.session.commit()
            flash('Avaliação adicionada com sucesso!', 'success')
            return redirect(url_for('product_detail', id=product_id))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao salvar avaliação. Tente novamente.', 'error')
    
    return render_template('add_review.html', form=form, product=product)

@app.route('/reviews/<int:product_id>')
def product_reviews(product_id):
    """Show all reviews for a product"""
    product = Product.query.get_or_404(product_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    reviews = Review.query.filter_by(product_id=product_id)\
                         .order_by(Review.created_at.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('product_reviews.html', product=product, reviews=reviews)

@app.route('/seller_reviews/<int:seller_id>')
def seller_reviews(seller_id):
    """Show all reviews for a seller"""
    seller = User.query.get_or_404(seller_id)
    if seller.user_type != 'produtor':
        flash('Usuário não é um produtor.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    reviews = Review.query.filter_by(seller_id=seller_id)\
                         .order_by(Review.created_at.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('seller_reviews.html', seller=seller, reviews=reviews)

@app.route('/my_reviews')
@login_required
def my_reviews():
    """Show reviews given by current user"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    reviews = Review.query.filter_by(reviewer_id=current_user.id)\
                         .order_by(Review.created_at.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('my_reviews.html', reviews=reviews)

@app.route('/delete_review/<int:review_id>')
@login_required
def delete_review(review_id):
    """Delete a review (only by the reviewer)"""
    review = Review.query.get_or_404(review_id)
    
    if review.reviewer_id != current_user.id:
        flash('Você só pode excluir suas próprias avaliações.', 'error')
        return redirect(url_for('my_reviews'))
    
    try:
        product_id = review.product_id
        db.session.delete(review)
        db.session.commit()
        flash('Avaliação excluída com sucesso.', 'success')
        return redirect(url_for('product_detail', id=product_id))
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir avaliação.', 'error')
        return redirect(url_for('my_reviews'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            try:
                # Generate reset token
                token = user.generate_reset_token()
                db.session.commit()
                
                # Generate reset URL for WhatsApp
                reset_url = url_for('reset_password', token=token, _external=True)
                
                # Get user's phone number from database
                user_phone = user.phone
                if not user_phone:
                    flash('Número de telefone não cadastrado. Por favor, atualize seu perfil com um número de WhatsApp.', 'error')
                    return redirect(url_for('forgot_password'))
                
                # Clean phone number (remove any formatting)
                import re
                clean_phone = re.sub(r'[^\d]', '', user_phone)
                
                # Ensure phone has country code (Brazil +55)
                if not clean_phone.startswith('55'):
                    if clean_phone.startswith('0'):
                        clean_phone = '55' + clean_phone[1:]  # Remove leading 0 and add country code
                    else:
                        clean_phone = '55' + clean_phone  # Add country code
                
                # Create WhatsApp message
                whatsapp_message = f"🔑 *Vale&feira - Recuperação de Senha*\n\nOlá! Aqui está seu link para redefinir a senha:\n\n{reset_url}\n\n⚠️ *Importante:* Este link expira em 1 hora por segurança.\n\nSe você não solicitou esta recuperação, ignore esta mensagem."
                
                # URL encode the message for WhatsApp
                import urllib.parse
                encoded_message = urllib.parse.quote(whatsapp_message)
                whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
                
                flash(f'Link de recuperação será enviado para o WhatsApp {user_phone}. Clique no botão para enviar.', 'success')
                return render_template('forgot_password.html', form=form, 
                                     reset_link=reset_url, 
                                     whatsapp_url=whatsapp_url,
                                     user_phone=user_phone,
                                     show_whatsapp_option=True)
                
            except Exception as e:
                db.session.rollback()
                flash('Erro ao processar solicitação. Tente novamente.', 'error')
        else:
            # Don't reveal if email exists or not for security
            flash('Se o email estiver cadastrado, você receberá um link de redefinição.', 'info')
            return redirect(url_for('login'))
    
    return render_template('forgot_password.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Find user by token
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash('Link de redefinição inválido ou expirado.', 'error')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            # Update password and clear token
            user.set_password(form.password.data)
            user.clear_reset_token()
            db.session.commit()
            
            flash('Sua senha foi redefinida com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao redefinir senha. Tente novamente.', 'error')
    
    return render_template('reset_password.html', form=form, token=token)

@app.route('/email_preview')
def email_preview():
    """Show email template preview"""
    return render_template('email_preview.html')

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Favorites routes
@app.route('/toggle_favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    """Toggle favorite status for a product"""
    product = Product.query.get_or_404(product_id)
    
    # Check if already favorited
    favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if favorite:
        # Remove from favorites
        db.session.delete(favorite)
        action = 'removed'
        flash('Produto removido dos favoritos!', 'success')
    else:
        # Add to favorites
        favorite = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(favorite)
        action = 'added'
        flash('Produto adicionado aos favoritos!', 'success')
    
    db.session.commit()
    
    # Return JSON for AJAX requests
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': True,
            'action': action,
            'is_favorited': action == 'added'
        })
    
    return redirect(request.referrer or url_for('products'))


@app.route('/favorites')
@login_required
def favorites():
    """Show user's favorite products"""
    page = request.args.get('page', 1, type=int)
    
    favorites_query = db.session.query(Product).join(Favorite).filter(
        Favorite.user_id == current_user.id
    ).order_by(Favorite.created_at.desc())
    
    # Get all favorites and manually paginate
    all_favorites = favorites_query.all()
    per_page = 12
    total = len(all_favorites)
    start = (page - 1) * per_page
    end = start + per_page
    favorites_items = all_favorites[start:end]
    
    # Create simple pagination object
    class SimplePagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.prev_num = page - 1 if self.has_prev else None
            self.has_next = page < self.pages
            self.next_num = page + 1 if self.has_next else None
            
        def iter_pages(self):
            for num in range(1, self.pages + 1):
                yield num
    
    favorites_paginated = SimplePagination(page, per_page, total, favorites_items)
    
    return render_template('favorites.html', 
                         favorites=favorites_paginated.items,
                         pagination=favorites_paginated,
                         title='Meus Favoritos')


# Analytics routes for producers
@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard for producers"""
    if current_user.user_type != 'produtor':
        flash('Acesso negado. Apenas produtores podem ver analytics.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get date range from request (default to last 30 days)
    from datetime import datetime, timedelta
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Basic metrics
    total_products = Product.query.filter_by(seller_id=current_user.id, is_active=True).count()
    total_chats = Chat.query.filter_by(receiver_id=current_user.id).count()
    total_reviews = Review.query.filter_by(seller_id=current_user.id).count()
    avg_rating = current_user.get_average_rating()
    
    # Product performance
    products_with_stats = db.session.query(
        Product,
        db.func.count(Chat.id).label('chat_count'),
        db.func.count(Favorite.id).label('favorite_count'),
        db.func.count(Review.id).label('review_count')
    ).outerjoin(Chat, Product.id == Chat.product_id)\
     .outerjoin(Favorite, Product.id == Favorite.product_id)\
     .outerjoin(Review, Product.id == Review.product_id)\
     .filter(Product.seller_id == current_user.id)\
     .group_by(Product.id)\
     .order_by(db.func.count(Chat.id).desc())\
     .limit(10).all()
    
    # Monthly chat trends (last 6 months) - PostgreSQL compatible
    monthly_chats = db.session.query(
        db.func.to_char(Chat.created_at, 'YYYY-MM').label('month'),
        db.func.count(Chat.id).label('count')
    ).filter(
        Chat.receiver_id == current_user.id,
        Chat.created_at >= start_date - timedelta(days=150)  # 6 months
    ).group_by(db.func.to_char(Chat.created_at, 'YYYY-MM'))\
     .order_by(db.func.to_char(Chat.created_at, 'YYYY-MM')).all()
    
    # Category performance
    category_stats = db.session.query(
        Product.category,
        db.func.count(Product.id).label('product_count'),
        db.func.count(Chat.id).label('chat_count'),
        db.func.avg(Review.rating).label('avg_rating')
    ).outerjoin(Chat, Product.id == Chat.product_id)\
     .outerjoin(Review, Product.id == Review.product_id)\
     .filter(Product.seller_id == current_user.id)\
     .group_by(Product.category)\
     .order_by(db.func.count(Chat.id).desc()).all()
    
    # Convert Row objects to dictionaries for JSON serialization
    monthly_chats_data = [{'month': row.month, 'count': row.count} for row in monthly_chats]
    category_stats_data = [
        {
            'category': row.category,
            'product_count': row.product_count,
            'chat_count': row.chat_count or 0,
            'avg_rating': float(row.avg_rating) if row.avg_rating else 0
        } 
        for row in category_stats
    ]
    
    return render_template('analytics.html',
                         total_products=total_products,
                         total_chats=total_chats,
                         total_reviews=total_reviews,
                         avg_rating=avg_rating,
                         products_with_stats=products_with_stats,
                         monthly_chats=monthly_chats_data,
                         category_stats=category_stats_data,
                         title='Analytics')
