(require! "stdlib.cl")

(defrec factorial (n)
  (if (= n 0)
      1
    (* n (factorial (- n 1)))
    )
  )

(print! "5! =" (factorial 5))
(print! (append '(1 2 3) '("d" "e" "f")))

(let
    (l '(1 2 3))
  (begin
   (print! "sum of" l "=" (sum l))
   )
  )

