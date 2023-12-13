async function createDeck() {
    let deckName = prompt("Enter the deck name");
    deckName = {name: deckName};
    
    await fetch("/add_deck", {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(deckName)
    })

    location.reload();
    return false;
}