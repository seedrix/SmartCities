(define (domain Guidance)
    (:requirements :typing :universal-preconditions)
    (:types shop shop_list – object)        
    (:predicates
        (at-shop ?x – shop_list ?y – shop)
        (shop-set ?x – shop_list)

    ; (:functions (people-at-shop ?x - shop) - number        

    ; (:action set_day
    ; :parameters (?x - shop_list ?y – shop)
    ; :precondition (not (shop-set ?x))
    ; :effect (and (shop-set ?x)
    ;            (at-shop ?x ?y)
    ;            (increase (people-at-shop ?y))
    ;         )
    ; )
)

