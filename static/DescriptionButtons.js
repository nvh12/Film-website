const likeButton = document.getElementById('like');
const dislikeButton = document.getElementById('dislike');
const libraryButton = document.getElementById('libraryButton');

likeButton.addEventListener('click', function () {
    movieTitle = this.getAttribute('data-movie-title');
    state = this.getAttribute('state');
    sendAction(movieTitle, 'like', state);
});
dislikeButton.addEventListener('click', function () {
    movieTitle = this.getAttribute('data-movie-title');
    state = this.getAttribute('state');
    sendAction(movieTitle, 'dislike', state);
});
libraryButton.addEventListener('click', function () {
    movieTitle = this.getAttribute('data-movie-title');
    action = this.getAttribute('action');
    state = this.getAttribute('state');
    sendAction(movieTitle, action, state);
});


function flashMessage(message, category = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `aler alert-${category}`;
    messageDiv.style.cssText = `
        position: fixed;
        top: 0;
        z-index: 9999;
        background-color: darkcyan;
        color: white;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: fadeout 5s forwards;
        max-width: 100%;
    `;
    messageDiv.innerHTML = `
    ${message}
    <button type="button" class="close-btn" aria-label="Close" onclick="this.parentElement.style.display='none';" style="
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            margin-left: 0px;
          ">
      <span aria-hidden="true">&times;</span>
    </button>
    `;
    document.body.appendChild(messageDiv);
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

function sendAction(movieTitle, action, state) {
    if(state === 'True'){
        fetch(`/description/${movieTitle}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action, state: state })
        })
            .then(response => response.json())
            .then(data => {
                flashMessage(data.message, 'success');
                const reactionElement = document.getElementById(`movie-reactions`);
                reactionElement.textContent = `Likes: ${data.likes} | Dislikes: ${data.dislikes}`;
                if (action === 'add') {
                    libraryButton.setAttribute('action', 'remove');
                    libraryButton.innerHTML = '<i class="fa-solid fa-plus"></i> Remove from library';
                } else if (action === 'remove') {
                    libraryButton.setAttribute('action', 'add');
                    libraryButton.innerHTML = '<i class="fa-solid fa-plus"></i> Add to library';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                flashMessage('An error occurred. Please try again.', 'danger');
            });
    }
    else{
        flashMessage('Log in to access features', 'info');
    }
}