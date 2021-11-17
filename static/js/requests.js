function follow(e, username) {
    e.preventDefault();
    e.stopPropagation();
    console.log(window.location.origin + '/@'+username+'/follow')
    fetch(window.location.origin + '/@'+username+'/follow')
        .then(response => {
            console.log(response)
            return response.json()
        })
        .then(data => {
            console.log(e.target.innerHTML)
            generateMessage(data.action)
            console.log(data.action.startsWith('Followed'))
            if (data.action.startsWith('Unfollowed')) {
                e.target.innerHTML = 'Follow <ion-icon name="add-circle-outline" role="img" class="md hydrated" aria-label="add circle outline"></ion-icon>'
            }
            else if (data.action.startsWith('Followed')) {
                e.target.innerHTML = 'Unfollow <ion-icon name="remove-circle-outline" role="img" class="md hydrated" aria-label="remove circle outline"></ion-icon>'
            }
        })
        .catch(err => {
            console.log(err)
        });
}