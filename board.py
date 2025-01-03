from flask import *
from projectDB import *
from logging_conf import *

blueprint = Blueprint('board', __name__, url_prefix='/board' ,template_folder='templates')

# 게시판 페이지(ID, 게시글, 작성 시간, 수정 시간) + 검색 포함
@blueprint.route('/view', methods=['GET', 'POST'])
def view():
    search_query = request.form.get('search', '').strip() if request.method == 'POST' else ''  # POST 요청에서만 검색어 가져오기
    if search_query:  # 검색어가 있으면 해당 제목의 글만 조회
        posts = PostDao().search_posts_by_title(search_query)
        board_logger.info(f'{search_query} 조회')
    else:
        posts = PostDao().get_all_posts()  # 검색어가 없으면 전체 글 조회
        board_logger.info('전체 상품 조회')
    return render_template('board.html', posts=posts, search_query=search_query)

# 게시글 추가 페이지
@blueprint.route('/newPost', methods=['GET', 'POST'])
def newPost():
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('로그인 후에 게시글을 작성할 수 있습니다.')
        return redirect(url_for('user.login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')
        
        if user_id:  # 사용자가 로그인된 경우
            PostDao().insert_post(user_id, title, content)
            flash('게시글이 성공적으로 작성되었습니다.')
            product_logger.info(f'userId : {user_id} title : {title} 등록')
            return redirect(url_for('board.view'))
        else:
            flash('로그인 후에 게시글을 작성할 수 있습니다.')
            product_logger.warning('로그인 필요')
            return redirect(url_for('user.login'))
    return render_template('newPost.html')


# 게시글 조회 페이지 select 추가 처리 필요
@blueprint.route('/viewPost/<int:post_id>')
def viewPost(post_id):
    post = PostDao().get_post_by_id(post_id)
    comments = PostDao().get_comments_by_post_id(post_id)  # 댓글 조회
    if post:
        user_name = UserDao().get_user_by_id(post['user_id'])['user_name']
        product_logger.info('게시글 조회')
        return render_template('viewPost.html', post=post, user_name=user_name, comments=comments)
    else:
        flash('해당 게시글을 찾을 수 없습니다.')
        product_logger.error('존재하지 않는 게시글')
        return redirect(url_for('board.view'))
    
# 게시글 수정 페이지
@blueprint.route('/editPost/<int:post_id>', methods=['GET', 'POST'])
def editPost(post_id):
    post = PostDao().get_post_by_id(post_id)
    
    # 게시글이 존재하는지 확인
    if not post:
        flash('해당 게시글을 찾을 수 없습니다.')
        product_logger.error('존재하지 않는 게시글')
        return redirect(url_for('board.view'))
    
    # 수정 요청 처리
    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        PostDao().update_post(post_id, new_title, new_content)
        flash('게시글이 성공적으로 수정되었습니다.')
        product_logger.info(f'{post_id} 수정')
        return redirect(url_for('board.viewPost', post_id=post_id))
    
    return render_template('editPost.html', post=post)

# 댓글 추가 라우트
@blueprint.route('/addComment/<int:post_id>', methods=['POST'])
def addComment(post_id):
    if 'user_id' not in session:
        flash('로그인 후에 댓글을 작성할 수 있습니다.')
        product_logger.warning('로그인 필요')
        return redirect(url_for('user.login'))

    content = request.form['content']
    user_id = session['user_id']
    PostDao().insert_comment(post_id, user_id, content)
    flash('댓글이 성공적으로 추가되었습니다.')
    product_logger.info(f'userID : {user_id}, content : {content}')
    return redirect(url_for('board.viewPost', post_id=post_id))

# 댓글 삭제 라우트 (작성자만 삭제 가능)
@blueprint.route('/deleteComment/<int:comment_id>', methods=['POST'])
def deleteComment(comment_id):
    # 세션의 사용자 ID와 댓글의 사용자 ID가 일치하는지 확인 필요
    PostDao().delete_comment(comment_id)
    flash('댓글이 삭제되었습니다.')
    product_logger.info(f'{comment_id} 삭제')
    return redirect(request.referrer)
