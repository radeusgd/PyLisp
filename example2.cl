(require! "stdlib.cl")
(print! "Guess my number!")
(define! mynumber (randint! 0 100))
(defrec run ()
  (begin
   (print! "Your guess:")
   (let (guess (str2int (readline!)))
     (if (= mynumber guess)
         (print! "You are right")
       (begin
        (print! (if (< mynumber guess) "Go smaller" "Go bigger"))
        (run)
        )))))

(run)
