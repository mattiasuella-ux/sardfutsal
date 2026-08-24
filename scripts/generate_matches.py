# Individua la primissima "Prossima Partita" in ordine cronologico
first_next_found = False

for match in matches:
    # ... [tutta la tua logica di parsing data e gol rimane identica] ...

    extra_card_class = ""

    if (
        sard_goals_value == -2
        and opponent_goals_value == -2
    ):
        match_label = "CALENDARIO IN AGGIORNAMENTO"
        score = ""
        # ... [tua logica card aggiornamento] ...

    elif (
        sard_goals_value >= 0
        and opponent_goals_value >= 0
    ):
        match_label = "RISULTATO FINALE"
        score = f"{sard_goals_value} - {opponent_goals_value}"

    else:
        # È una partita futura
        if not first_next_found:
            match_label = "PROSSIMO IMPEGNO • NEXT MATCH"
            extra_card_class = "is-next-match"  # <--- CLASSE SPECIALE
            first_next_found = True
        else:
            match_label = "PROSSIMA PARTITA"
        
        score = "VS"

    # ... [tua logica Casa / Trasferta e Loghi] ...

    # Nella generazione della card, aggiungi la classe extra_card_class:
    card = f"""
    <div class="match-card-wrapper {extra_card_class}">

        <div class="match-card-label">
            {match_label}
        </div>

        <article class="match-card">
            <!-- Tutto il resto del tuo HTML generato invariato -->
        </article>

    </div>
    """

    cards.append(card)
