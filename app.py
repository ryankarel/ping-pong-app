from flask import Flask, render_template, flash, redirect, url_for
from config import Config
from models import Player, Game, db
from forms import RegistrationForm, LoginForm, SubmitGameForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return Player.query.get(int(id))

@app.route('/')
@app.route('/index')
@login_required
def index():
    games = current_user.games.order_by(Game.timestamp.desc()).all()
    return render_template('index.html', title='Home', games=games)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Player(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Player.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
# Add this new route to app.py
@app.route('/submit_game', methods=['GET', 'POST'])
@login_required
def submit_game():
    form = SubmitGameForm()
    if form.validate_on_submit():
        player = Player.query.filter_by(username=form.player_username.data).first()
        opponent = Player.query.filter_by(username=form.opponent_username.data).first()
        if player is None or opponent is None:
            flash('Invalid player or opponent username')
            return redirect(url_for('submit_game'))
        game = Game(player_id=player.id, opponent_id=opponent.id,
                    player_score=form.player_score.data, opponent_score=form.opponent_score.data)
        db.session.add(game)
        db.session.commit()
        flash('New game submitted')
        return redirect(url_for('submit_game'))
    return render_template('submit_game.html', form=form)
    
@app.route('/view_games')
@login_required
def view_games():
    games = Game.query.order_by(Game.timestamp.desc()).all()
    return render_template('view_games.html', games=games)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
