(define! defun (macro (name args body)
  (list 'define! name (list 'fun args body))
  ))

(define! defmacro (macro (name args body)
                         (list 'define! name (list 'macro args body))
                         ))
(defun id (x) x)
(defmacro defrec (name args body)
  (list define! name
        (list 'letrec
              (list (list name (list 'fun args body)))
              name)
        ))

(defrec map (f list)
  (if (= list nil)
      nil
    (cons (f (head list)) (map f (tail list)))
    ))

(defrec append (l1 l2)
  (if (= l1 nil)
      l2
    (cons (head l1) (append (tail l1) l2))
    )
  )
