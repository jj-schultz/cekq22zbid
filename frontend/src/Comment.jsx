import './scss/Comment.scss'
import {formatDate} from './lib/utils.js';

function Comment({comment, onEdit, onDelete}) {
    return (
        <div className="comment">
            <div className="comment-header">
                <span className="comment-author">{comment.author.name}</span>
                <div className="comment-header-right">
                    <div
                        className="comment-date"
                    >{formatDate(comment.created_date)}</div>
                    <a
                        onClick={() => onEdit(comment)}
                        className="edit-comment-btn"
                        title="Edit Comment"
                    >&#9998;</a>
                    <a
                        onClick={() => onDelete(comment)}
                        className="edit-comment-btn"
                        title="Delete Comment"
                    >&#128465;</a>
                </div>
            </div>
            {comment.image && (
                <div className="comment-image">
                    <img
                        src={comment.image}
                        alt="comment image"
                        onError={(e) => {
                            e.target.style.display = 'none';
                        }}
                    />
                </div>
            )}
            <div className="comment-text">{comment.text}</div>
            <div className="comment-footer">
                <span className="comment-likes">❤️ {comment.likes}</span>
            </div>
        </div>
    );
}

export default Comment;
