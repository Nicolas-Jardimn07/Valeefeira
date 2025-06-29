from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, DateField, PasswordField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError
import re
from wtforms.widgets import TextArea

class RegistrationForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[
        DataRequired(message='Nome de usuário é obrigatório'),
        Length(min=4, max=20, message='Nome de usuário deve ter entre 4 e 20 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória'),
        Length(min=6, message='Senha deve ter pelo menos 6 caracteres')
    ])
    password2 = PasswordField('Confirmar senha', validators=[
        DataRequired(message='Confirmação de senha é obrigatória'),
        EqualTo('password', message='Senhas não coincidem')
    ])
    user_type = SelectField('Tipo de usuário', choices=[
        ('produtor', 'Produtor'),
        ('comprador', 'Comprador')
    ], validators=[DataRequired(message='Tipo de usuário é obrigatório')])
    cpf = StringField('CPF', validators=[
        DataRequired(message='CPF é obrigatório'),
        Length(min=11, max=11, message='CPF deve ter 11 dígitos')
    ])
    phone = StringField('Telefone', validators=[Length(max=20)])
    city = SelectField('Cidade', choices=[], validators=[
        DataRequired(message='Cidade é obrigatória')
    ])

    description = TextAreaField('Descrição/Sobre', validators=[Length(max=1000)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória')
    ])

class ProductForm(FlaskForm):
    name = StringField('Nome do produto', validators=[
        DataRequired(message='Nome do produto é obrigatório'),
        Length(max=100, message='Nome muito longo')
    ])
    description = TextAreaField('Descrição', validators=[
        DataRequired(message='Descrição é obrigatória'),
        Length(max=1000, message='Descrição muito longa')
    ], widget=TextArea())
    category = SelectField('Categoria', choices=[
        ('frutas', 'Frutas'),
        ('verduras', 'Verduras'),
        ('legumes', 'Legumes'),
        ('cereais', 'Cereais'),
        ('lacteos', 'Laticínios'),
        ('carnes', 'Carnes'),
        ('artesanato', 'Artesanato'),
        ('outros', 'Outros')
    ], validators=[DataRequired(message='Categoria é obrigatória')])
    price = FloatField('Preço', validators=[
        DataRequired(message='Preço é obrigatório'),
        NumberRange(min=0.01, message='Preço deve ser maior que zero')
    ])
    unit = SelectField('Unidade', choices=[
        ('kg', 'Quilograma (kg)'),
        ('g', 'Grama (g)'),
        ('unidade', 'Unidade'),
        ('duzia', 'Dúzia'),
        ('caixa', 'Caixa'),
        ('saca', 'Saca'),
        ('litro', 'Litro'),
        ('metro', 'Metro')
    ], validators=[DataRequired(message='Unidade é obrigatória')])
    quantity_available = IntegerField('Quantidade disponível', validators=[
        DataRequired(message='Quantidade é obrigatória'),
        NumberRange(min=1, message='Quantidade deve ser maior que zero')
    ])
    image = FileField('Imagem do produto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')
    ])
    is_organic = BooleanField('Produto orgânico')
    harvest_date = DateField('Data da colheita', validators=[])

class SearchForm(FlaskForm):
    query = StringField('Buscar produtos', validators=[Length(max=100)])
    category = SelectField('Categoria', choices=[
        ('', 'Todas as categorias'),
        ('frutas', 'Frutas'),
        ('verduras', 'Verduras'),
        ('legumes', 'Legumes'),
        ('cereais', 'Cereais'),
        ('lacteos', 'Laticínios'),
        ('carnes', 'Carnes'),
        ('artesanato', 'Artesanato'),
        ('outros', 'Outros')
    ])
    city = SelectField('Cidade', choices=[])

class ChatForm(FlaskForm):
    message = TextAreaField('Mensagem', validators=[
        DataRequired(message='Mensagem é obrigatória'),
        Length(max=1000, message='Mensagem muito longa')
    ], render_kw={"rows": 3, "placeholder": "Digite sua mensagem..."})

class ReviewForm(FlaskForm):
    rating = SelectField('Avaliação', choices=[
        ('5', '★★★★★ (5) - Excelente'),
        ('4', '★★★★☆ (4) - Muito bom'),
        ('3', '★★★☆☆ (3) - Bom'),
        ('2', '★★☆☆☆ (2) - Regular'),
        ('1', '★☆☆☆☆ (1) - Ruim')
    ], validators=[DataRequired(message='Avaliação é obrigatória')])
    
    title = StringField('Título da avaliação', validators=[
        Length(max=200, message='Título muito longo')
    ], render_kw={"placeholder": "Resumo da sua experiência..."})
    
    comment = TextAreaField('Comentário', validators=[
        Length(max=1000, message='Comentário muito longo')
    ], render_kw={
        "rows": 4, 
        "placeholder": "Conte sobre sua experiência com este produto e vendedor..."
    })

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido')
    ], render_kw={"placeholder": "Digite seu email cadastrado"})

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova senha', validators=[
        DataRequired(message='Nova senha é obrigatória'),
        Length(min=6, message='Senha deve ter pelo menos 6 caracteres')
    ])
    password2 = PasswordField('Confirmar nova senha', validators=[
        DataRequired(message='Confirmação de senha é obrigatória'),
        EqualTo('password', message='Senhas não coincidem')
    ])

class EditProfileForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[
        DataRequired(message='Nome de usuário é obrigatório'),
        Length(min=4, max=20, message='Nome de usuário deve ter entre 4 e 20 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido')
    ])
    phone = StringField('Telefone', validators=[Length(max=20)])
    city = SelectField('Cidade', choices=[], validators=[
        DataRequired(message='Cidade é obrigatória')
    ])
    description = TextAreaField('Descrição/Sobre', validators=[Length(max=1000)])
    profile_image = FileField('Foto de perfil', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')
    ])
    
    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        
        # Populate city choices
        from utils import get_cities
        cities = get_cities()
        self.city.choices = [('', 'Selecione uma cidade')] + [(city, city) for city in cities]
    
    def validate_username(self, username):
        if username.data != self.original_username:
            from models import User
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Nome de usuário já está em uso.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            from models import User
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email já está em uso.')
