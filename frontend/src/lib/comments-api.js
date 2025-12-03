import {doGet, doPost} from './utils.js';


async function fetchComments() {
    const response = await doGet(`/api/v1/comments/`);
    return response.comments;
}

async function upsertComment({comment_id, text, image}) {
    return await doPost(`/api/v1/comments/upsert/`, {
        comment_id,
        text,
        image
    });
}

async function deleteComment({commentId}) {
    return await doPost(`/api/v1/comments/${commentId}/delete/`);
}


export {fetchComments, upsertComment, deleteComment};
