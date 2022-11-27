Require Import Coq.micromega.Psatz.
Require Import Coq.Strings.Ascii.
Require Import Coq.Strings.String.
Require Import Coq.Logic.Classical_Prop.
Require Import PL.SetsDomain.
Require Import PL.CoqInductiveType.
Require Import PL.SemanticsIntro.
Local Open Scope string.
Local Open Scope sets_scope.

(** **** Exercise **** *)
(** 请证明下面性质_[arith_ex]_。*)

Example arith_ex: forall n m: nat,
  n = 1 \/ m = 1 -> n = n * m \/ m = n * m.
Proof.
  intros.
  destruct H as [Hn | Hm].
  + right.
      lia.
  + left.
      lia.
Qed.

(** **** Exercise **** *)
(** 请证明下面关于逻辑的引理_[forall_K]_。提示：可以尝试下面的证明指令：

      _[specialize (H x)]_

      _[specialize (H x H0)]_

      _[pose proof H x]_

      _[pose proof H x H0]_

      _[apply H]_ *)

Lemma forall_K: forall (A: Type) (P Q: A -> Prop),
  (forall x, P x -> Q x) ->
  (forall x, P x) -> (forall x, Q x).  
Proof.
  intros.
  apply H.
  apply H0.
Qed.

(** **** Exercise **** *)
(** 请证明下面关于逻辑的引理_[forall_not_not_forall]_。*)

Lemma forall_not_not_exists: forall (A: Type) (P: A -> Prop),
  (forall x, ~ P x) ->
  ~ exists x, P x.
Proof.
  intros.
  pose proof classic (exists x: A, P x).
  destruct H0.
  + destruct H0.
      specialize (H x).
      contradiction.
  + exact H0.
Qed.
      

(** **** Exercise **** *)
(** 请证明下面关于集合的引理_[included_irreflexive]_。*)

Lemma included_irreflexive: forall (A: Type) (P Q: A -> Prop),
  P ⊆ Q -> Q ⊆ P -> P == Q.
Proof.
  intros A P Q.
  sets_unfold.
  intros.
  split; intros.
  + apply H in H1.
      exact H1.
  + apply H0 in H1.
      exact H1.
Qed.

(** **** Exercise **** *)
(** 请证明下面关于字符串集合的引理_[string_set_app_union_distr]_。*)

Lemma string_set_app_union_distr_l: forall X Y Z: string -> Prop,
  X ∘ (Y ∪ Z) == (X ∘ Y) ∪ (X ∘ Z).
Proof.
  intros.
  unfold string_set_app; sets_unfold.
  intros.
  split.
  + intros.
      destruct H as [?[?[?[? ?]]]].
      destruct H0.
      * left.
         exists x, x0.
         auto.
      * right.
         exists x, x0.
         auto.
  + intros.
      destruct H.
      * destruct H as [?[?[?[? ?]]]].
         exists x, x0.
          auto.
      * destruct H as [?[?[?[? ?]]]].
         exists x, x0.
         auto.
Qed.
           
