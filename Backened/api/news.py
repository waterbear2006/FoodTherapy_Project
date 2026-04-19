from flask import Blueprint, jsonify
from services.news import get_food_news

news_bp = Blueprint('news', __name__)

@news_bp.route('/api/news', methods=['GET'])
def news_list():
    news = get_food_news()
    return jsonify({
        "code": 200,
        "data": news
    })