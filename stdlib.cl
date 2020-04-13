(define! id (fun (x) x))

(define! tst 42)
(define! make_adder (fun (a) (fun (b) (+ a b))))

(define! map (letrec
                 ((recmap
                   (fun (f list)
                        (if (= list nil)
                            nil
                          (cons (f (head list)) (recmap f (tail list)))
                   ))
                   ))
               recmap
               ))
