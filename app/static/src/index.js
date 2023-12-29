async function add_deck() {
    let deck_name = prompt("Enter the name for the deck");
    deck_name = {name: deck_name};
    
    await fetch("/add_deck", {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(deck_name)
    })

    location.reload();
    return false;
}

function change_card_state() {
    let button = document.querySelector('#card_state');
    let card_back = document.querySelector('#card_back')

    if (button.innerText == 'Show') {
        button.innerHTML = 'Hide';
        card_back.classList.remove('hidden')
    }
    else {
        button.innerHTML = "Show";
        card_back.classList.add('hidden')
    }
}