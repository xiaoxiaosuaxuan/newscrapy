Require Import Coq.ZArith.ZArith.
Require Import Coq.micromega.Psatz.
Require Import Coq.Strings.Ascii.
Require Import Coq.Strings.String.
Require Import PL.CoqInductiveType.
Local Open Scope Z.
Local Open Scope string.

(** **** Exercise **** *)
(** 请证明下面引理_[size_nonneg]_。*)

Lemma size_nonneg: forall t,
  0 <= tree_size t.
Proof.
  intros.
  induction t.
  + simpl.
      lia.
  + simpl.
      lia.
Qed.


(** **** Exercise **** *)
(** 下面定义的_[left_most]_与_[right_most]_函数分别计算了二叉树中最左边的节点编
    号以及最右边的节点编号。如果树是空树，则返回_[default]_参数。请证明下面引理
    _[left_most_reverse]_。*)

Fixpoint left_most (t: tree) (default: Z): Z :=
  match t with
  | Leaf => default
  | Node l n r => left_most l n
  end.

Fixpoint right_most (t: tree) (default: Z): Z :=
  match t with
  | Leaf => default
  | Node l n r => right_most r n
  end.

(** 提示：如果你的前两步证明指令是_[intros]_以及_[induction t]_，那么你会发现，
    归纳步骤的结论是无法证明的。你会发现你需要使用的_[default]_参数与归纳假设中
    的不一致。你可以尝试用_[intros t]_以及_[induction t]_开始你的证明，看看有什
    么不同。*)

Lemma left_most_reverse: forall t default,
  left_most (tree_reverse t) default = right_most t default.
Proof.
  intros t.
  induction t.
  + simpl.
      reflexivity.
  + intros default.
      simpl.
      rewrite IHt2.
      reflexivity.
Qed.


(** **** Exercise **** *)
(** 下面定义的_[string_rev_append]_是一种用尾递归方法定义字符串左右翻转的方法。
    请你证明它与我们先前定义的_[string_rev]_之间的关系。  *)

Fixpoint string_rev_append (s1 s2: string): string :=
  match s1 with
  | EmptyString => s2
  | String c s1' => string_rev_append s1' (String c s2)
  end.

Lemma string_rev_append_spec: forall s1 s2: string,
  string_rev_append s1 s2 = string_app (string_rev s1) s2.
Proof.
  intros s1.
  induction s1.
  + simpl.
      reflexivity.
  + simpl.
      intros s2.
      replace (string_app (string_app (string_rev s1) (String a "")) s2) with 
                  (string_app (string_rev s1) (String a s2)).

      * apply IHs1 with (s2 := String a s2).
      * rewrite <- string_app_assoc.
         simpl. 
         reflexivity.
Qed.















