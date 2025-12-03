const API_BASE_URL = import.meta.env.VITE_API_BASE


async function doGet(url) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
        credentials: 'include'
    });
    
    const resp_data = await response.json();
    
    if (!response.ok) {
        throw new Error(resp_data.error || `HTTP error! status: ${response.status}`);
    }

    return resp_data;
}

async function doPost(url, data = {}) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data)
    });

    const resp_data = await response.json();
    
    if (!response.ok) {
        throw new Error(resp_data.error || `HTTP error! status: ${response.status}`);
    }

    return resp_data;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

export {formatDate, doGet, doPost};
