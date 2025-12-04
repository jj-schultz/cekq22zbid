import './scss/App.scss'
import './scss/CommentModal.scss'
import Comment from './Comment'

import {useRef} from 'react'
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query'
import {useForm} from 'react-hook-form'
import {doPost, doGet} from "./lib/utils.js";

function App() {
    const queryClient = useQueryClient();
    const dialogRef = useRef(null);
    
    const {register, handleSubmit, reset, setValue, watch} = useForm({
        defaultValues: {comment_id: null, text: "", image: ""}
    });

    const commentUpsertMutation = useMutation({
        mutationFn: ({comment_id, text, image}) => {
            return doPost(`/api/v1/comments/upsert/`, {
                comment_id,
                text,
                image
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['comments']});
        },
    });

    const deleteMutation = useMutation({
        mutationFn: ({commentId}) => {
            return doPost(`/api/v1/comments/${commentId}/delete/`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ['comments']});
        },
    });

    const {data: comments = [], isLoading, error} = useQuery({
        queryFn: async () => {
            const response = await doGet(`/api/v1/comments/`);
            return response.comments;
        },
        queryKey: ['comments']
    });

    const handleDeleteComment = (comment) => {
        deleteMutation.mutate({
            commentId: comment.id
        });
    }

    const handleEditComment = (comment) => {
        setValue("comment_id", comment.id);
        setValue("text", comment.text);
        setValue("image", comment.image || "");
        dialogRef.current?.showModal();
    };

    const handleAddComment = () => {
        reset();
        dialogRef.current?.showModal();
    };


    const handleCancel = () => {
        reset();
        dialogRef.current?.close();
    };

    const handleCommentModalSubmit = async (data) => {
        try {
            await commentUpsertMutation.mutateAsync({
                comment_id: data.comment_id,
                text: data.text,
                image: data.image
            });
            reset();
            dialogRef.current?.close();
        } catch (err) {
            alert(`Failed to create comment: ${err.message}`);
        }
    };

    if (isLoading) {
        return <div className="loading">Loading comments...</div>;
    }

    if (error) {
        return <div className="error">Error loading comments: {error.message}</div>;
    }

    return (
        <div className="app">
            <div className="app-header">
                <h3>Comments</h3>
                <button onClick={handleAddComment} className="add-comment-btn">Add Comment</button>
            </div>

            <div className="comments-container">
                {
                    comments.length === 0
                        ? (<img className="no-comment-img" 
                                alt="No Comment"
                                src="https://t3.ftcdn.net/jpg/00/89/38/36/360_F_89383607_WPQtq9NF1O2Vvou7CT1WgjCtQooeXVju.jpg"/>)
                        : (
                            comments.map((comment) => (
                                <Comment
                                    key={comment.id}
                                    comment={comment}
                                    onEdit={handleEditComment}
                                    onDelete={handleDeleteComment}
                                />
                            ))
                        )
                }
            </div>

            <dialog ref={dialogRef} className="comment-modal">
                <form onSubmit={handleSubmit(handleCommentModalSubmit)} className="comment-form">
                    <h2>{watch("comment_id") ? "Edit Comment" : "Add Comment"}</h2>
                    <div className="form-group">
                        <textarea
                            id="comment-text"
                            {...register("text", {required: true})}
                            placeholder="Enter your comment..."
                            rows="5"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="image-link">Image Link (optional)</label>
                        <input
                            id="image-link"
                            type="url"
                            {...register("image")}
                            placeholder="https://example.com/image.jpg"
                        />
                    </div>
                    <div className="form-actions">
                        <button type="button" onClick={handleCancel} className="cancel-btn">
                            Cancel
                        </button>
                        <button type="submit" className="submit-btn">
                            Submit
                        </button>
                    </div>
                </form>
            </dialog>
        </div>
    )
}

export default App
