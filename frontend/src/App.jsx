import './scss/App.scss'
import './scss/CommentModal.scss'
import Comment from './Comment'

import {useMemo, useRef, useState} from 'react'
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query'
import {useForm} from 'react-hook-form'
import {doGet, doPost} from "./lib/utils.js";

function App() {
    const queryClient = useQueryClient();
    const dialogRef = useRef(null);
    const [searchString, setSearchString] = useState("");

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

    const commentsTree = useMemo(() => {
        comments.sort(
            (c1, c2) => {
                return parseInt(c1.id) - parseInt(c2.id)
            }
        );

        const commendsById = {}
        comments.forEach(c => {
            commendsById[c.id] = c;
        })

        // when I find a comment with text that contains search string
        // include the parent and all children deep

        const filteredComments = comments.filter(c => c.text.indexOf(searchString) >= 0);

        const commentTree = {}
        filteredComments.forEach(c => {
            const root_comment = c.parent_comment_id
                ? commendsById[c.parent_comment_id]
                : c;


            commendsById[c.id] = c;
            c.child_comments = [];
            if (!c.parent_comment_id) {
                commentTree[c.id] = c
            } else {
                commendsById[c.parent_comment_id].child_comments.push(c)
            }
        })
        
        return commentTree;
    }, [comments])

    const commentsByParentId = useMemo(() => {


        return comments.reduce((cbp, c) => {
            if (!cbp[c.parent_comment_id]) {
                cbp[c.parent_comment_id] = []
            }
            cbp[c.parent_comment_id].push(c)
            return cbp;
        }, {});

    }, [comments])

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

    const handleSearch = () => {
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

    const renderComments = (parent_comment = null, commentIndent = 0) => {
        const children = parent_comment
            ? parent_comment.child_comments
            : Object.values(commentsTree)
        ;

        if (!children) {
            return [];
        }

        return children.flatMap((comment) => [
            (
                <Comment
                    commentIndent={commentIndent}
                    key={comment.id}
                    comment={comment}
                    onEdit={handleEditComment}
                    onDelete={handleDeleteComment}
                />
            ),
            ...renderComments(comment, commentIndent + 1)]
        );
    }

    return (
        <div className="app">
            <div className="app-header">
                <h3>Comments</h3>
                {/*<input type="text" value={searchString} onChange={handleSearch} placeholder="Search"/>*/}
                <button onClick={handleAddComment} className="add-comment-btn">Add Comment</button>
            </div>

            <div className="comments-container">
                {
                    comments.length === 0
                        ? (<img className="no-comment-img"
                                alt="No Comment"
                                src="https://t3.ftcdn.net/jpg/00/89/38/36/360_F_89383607_WPQtq9NF1O2Vvou7CT1WgjCtQooeXVju.jpg"/>)
                        : (
                            renderComments()

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
