(define (problem week1)
    (:domain Guidance)
    (:objects shop1 shop2 shop3 - shop
        list1 list2 list3 list4 list5 - list)
    (:init
        (forall (?x - shop) (= (people-at-shop ?x) 0))
    (:goal 
        (and (forall (?x - shop_list) shop-set ?x)
            (forall (?x - shop) (<= (people-at-shop ?x) 2)
        )
)

