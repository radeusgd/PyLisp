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

(defrec fold (f zero lst)
  (if (= lst nil)
      zero
    (f (head lst) (fold f zero (tail lst)))
    )
  )

(defun append (l1 l2)
  (fold cons l2 l1))

(defun sum (lst) (fold + 0 lst))
