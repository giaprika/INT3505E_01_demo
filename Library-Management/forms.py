from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class BookForm(FlaskForm):
    title = StringField("Tên sách", validators=[DataRequired()])
    author = StringField("Tác giả", validators=[DataRequired()])
    submit = SubmitField("Thêm")

class BorrowForm(FlaskForm):
    borrower = StringField("Tên người mượn", validators=[DataRequired()])
    submit = SubmitField("Mượn sách")
