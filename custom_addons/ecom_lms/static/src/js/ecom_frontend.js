odoo.define("ecom_lms.ecomframe", function (require) {
    "use strict";

    var Screens = require('website_slides.quiz');
    console.log(Screens,"screnness")
    Screens.Quiz.include({
        _getQuizAnswers: function () {
//                var data=[]
//                var newvals = this.$('input[type=radio]:checked').val();
//                var checkvals = this.$('input[type=checkbox]:checked').val();
//                var numselect = this.$('input[id="text"]').val();
//                var charselect = this.$('input[id="textchar"]').val();
//                var chartext = this.$('input[id="textchar2"]').val();
//
//                console.log(newvals,"checkva12333newwwww");
//                console.log(datevals,"numvalssss");
//                      data.push(newvals,checkvals,numselect,charselect,chartext);
//                     return data;

                return this.$('input[type=radio]:checked').map(function (index, element) {
                    return parseInt($(element).val());
                }).get();
    //            console.log("return dataaaa")
            },


       _renderAnswersHighlightingAndComments: function () {
            var self = this;
            console.log("loggggggggggg")
            this.$('.o_wslides_js_lesson_quiz_question').each(function () {
                var $question = $(this);
                var questionId = $question.data('questionId');

                var isCorrect = self.quiz.answers[questionId].is_correct;

                var isCorrect = self.quiz.answers[questionId].is_correct;


                $question.find('a.o_wslides_quiz_answer').each(function () {
                    var $answer = $(this);
                    $answer.find('i.fa').addClass('d-none');
                    if ($answer.find('input[type=radio]')[0].checked) {

                        if (isCorrect) {
                            $answer.removeClass('list-group-item-danger').addClass('list-group-item-success');
                            $answer.find('i.fa-check-circle').removeClass('d-none');
                        } else {
                            $answer.removeClass('list-group-item-success').addClass('list-group-item-danger');
                            $answer.find('i.fa-times-circle').removeClass('d-none');
                            $answer.find('label input').prop('checked', false);
                        }

                        if (isCorrect) {
                            $answer.removeClass('list-group-item-danger').addClass('list-group-item-success');
                            $answer.find('i.fa-check-circle').removeClass('d-none');
                        } else {
                            $answer.removeClass('list-group-item-success').addClass('list-group-item-danger');
                            $answer.find('i.fa-times-circle').removeClass('d-none');
                            $answer.find('label input').prop('checked', false);
                        }

                    } else {
                        $answer.removeClass('list-group-item-danger list-group-item-success');
                        $answer.find('i.fa-circle').removeClass('d-none');
                    }
                });

                var comment = self.quiz.answers[questionId].comment;
                if (comment) {
                    $question.find('.o_wslides_quiz_answer_info').removeClass('d-none');
                    $question.find('.o_wslides_quiz_answer_comment').text(comment);
                }

                var comment = self.quiz.answers[questionId].comment;
                if (comment) {
                    $question.find('.o_wslides_quiz_answer_info').removeClass('d-none');
                    $question.find('.o_wslides_quiz_answer_comment').text(comment);
                }

            });
        },

    });
    });




