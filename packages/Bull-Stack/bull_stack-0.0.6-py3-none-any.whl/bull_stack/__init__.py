import os
import inspect
from dataclasses import dataclass
from collections import namedtuple
from flask import Blueprint, render_template, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import Form, FormField, FieldList, StringField, EmailField, SubmitField, SelectField, BooleanField, IntegerField, FloatField
from wtforms.validators import InputRequired, Optional
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry, relationship
from flask_bauto import AutoBlueprint

@dataclass
class BullStack:
    name: str
    blueprints: list
    config_filename: str = None
    tasks_enabled: bool = False
    brand_name: str = None
    logo: str = None
    index_page: str = 'base.html'
    index_redirect: bool = None
    secret_key: str = os.urandom(12).hex() # TODO field with default_factory, to save in location
    sql_db_uri: str = "sqlite:///:memory:"
    db_migration: bool = False
    admin_user: str = 'badmin'
    admin_email: str = None
    admin_init_password: str = None
    
    def create_app(self):
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_fefset import FEFset
        from flask_uxfab import UXFab
        from flask_iam import IAM
        #from sqlalchemy.orm import create_engine
        #engine = create_engine(DATABASE_URL, echo=True)
        self.app = Flask(self.name)

        # App configuration
        self.app.config["SQLALCHEMY_DATABASE_URI"] = self.sql_db_uri
        self.app.config['SECRET_KEY'] = self.secret_key
        self.app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # max 50MB upload
        if self.tasks_enabled:
            self.app.config.from_mapping(
                CELERY=dict(
                    broker_url=os.environ.get("CELERY_BROKER_URL"),#'sqla+sqlite:////tmp/celery.db'
                    result_backend=f"db+sqlite:///{os.path.join(self.app.instance_path,'shared/celery.db')}",
                    #os.environ.get("CELERY_RESULT_BACKEND", "rpc://"),
                    task_ignore_result=True,
                ),
            )
        if self.config_filename:
            self.app.config.from_pyfile(self.config_filename)

        # Instance dir
        if not os.path.exists(self.app.instance_path):
            self.app.logger.warning(
                'Instance path "%s" did not exist. Creating directory.',
                self.app.instance_path
            )
            os.makedirs(self.app.instance_path)
        
        # App extensions
        fef = FEFset(frontend='bootstrap4', role_protection=True)
        if self.brand_name: fef.settings['brand_name'] = self.brand_name
        if self.logo: fef.settings['logo_url'] = os.path.join('/static', self.logo)
        fef.init_app(self.app)
        uxf = UXFab()
        uxf.init_app(self.app)

        ## Database
        db = SQLAlchemy(self.app)
        # db migration
        if self.db_migration:
            from flask_migrate import Migrate
            from bull_stack.migrate import run_conditional_migration
            migrate = Migrate(self.app, db, render_as_batch=True, compare_type=False)
            #run_conditional_migration(self.app, db)

        ## User and role management
        iam = IAM(db)
        iam.init_app(self.app)
        with self.app.app_context():
            # These extensions do not auto-create tables
            # unlike AutoBlueprint
            db.create_all()
            # Check if admin user should be created
            if self.admin_init_password and not iam.models.User.query.count():
                iam.add_user(
                    self.admin_user, self.admin_email, self.admin_init_password
                )

        # Blueprint extensions
        for blueprint in self.blueprints:
            # First registering all models so blueprint models find each other
            blueprint.set_bauprint(registry=db.Model.registry)
        for blueprint in self.blueprints:
            blueprint.init_app(self.app)

            
        @self.app.errorhandler(500)
        def internal_error(error):
            return render_template('500.html'), 500
         
        @self.app.route('/', methods=['GET'])
        def index():
            if self.index_redirect: return redirect(self.index_redirect)
            else: return render_template(self.index_page)

        return self.app

    def __call__(self, *args, run=False, **kwargs):
        if run:
            try: self.run(*args, **kwargs)
            except AttributeError:
                self.create_app()
                self.run(*args, **kwargs)
        else: return self.create_app()
            
    def run(self, *args, **kwargs):
        return self.app.run(*args, **kwargs)
