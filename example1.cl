(require! "stdlib.cl")

(defrec factorial (n)
  (if (= n 0)
      1
    (* n (factorial (- n 1)))
    )
  )

(print! (factorial 5))
(print! (append '(1 2 3) '("d" "e" "f")))
