(define (problem week1)
    (:domain Guidance)
    (:objects shop1 shop2 shop3 - shop
        list1 list2 list3 list4 list5 - list)   
    (:init (= (people-at-shop shop1) 0)
        (= (people-at-shop shop2) 0)
        (= (people-at-shop shop3) 0)
        (shop-option list1 shop1)
        (shop-option list2 shop1)
        (shop-option list3 shop1)
        (shop-option list4 shop1)
        (shop-option list5 shop1)
    )
    (:goal 
        (and (list-set list1)
            (list-set list2)
            (list-set list3)
            (list-set list4)
            (list-set list5)
            (< (people-at-shop shop1) 2)            
        )
    )
)

