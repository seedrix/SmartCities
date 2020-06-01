(define (domain Guidance)
    (:requirements :typing :universal-preconditions)
    (:types shop shop_list – object        
        ; monday tuesday wednesday thursday friday saturday sunday - day)
    (:predicates
        ; (at-day ?x - shop_list ?y – day)
        ; (list-set ?x – shop_list)
        (at-shop ?x - shop_list ?y – shop)
        (shop-set ?x – shop_list)
        ; (free ?x – arm)
        ; (carry ?x – arm ?y – ball))

    (:functions (people-at-shop ?x - shop) - number        

    (:action set_day
    :parameters (?x - shop_list ?y – shop)
    :precondition (not (shop-set ?x))
    :effect (and (shop-set ?x)
               (at-shop ?x ?y)
               (increase (people-at-shop ?y))
            )
    )
)

