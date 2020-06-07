(define (domain Guidance)
    (:requirements [:typing] [:adl])
    (:types shop list – object)        
    (:predicates
        (at-shop ?x - list ?y - shop)
        (list-set ?x - list)
        (shop-option ?x - list ?y - shop)
    )

    (:functions (people-at-shop ?x - shop) - number)        

    (:action choose
        :parameters (?list -list ?shop -shop)
        :precondition (and (not (list-set ?list))
                            (shop-option ?list ?shop)
        )
        :effect (and (list-set ?list)
                   (at-shop ?list ?shop)
                   (increase (people-at-shop ?shop) 1)   
                )
    )
)

