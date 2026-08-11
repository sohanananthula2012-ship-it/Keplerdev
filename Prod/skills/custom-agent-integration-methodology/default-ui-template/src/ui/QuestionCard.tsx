import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ChevronDown, ChevronUp, CircleHelp } from 'lucide-react';
import type {
  BuilderPublicSiteLocaleInput,
  BuilderPublicSiteViewMessage,
  BuilderQuestion,
  BuilderQuestionAnswerEntry,
  BuilderQuestionAnswers,
} from '../core/types';
import { questionCardLabels } from '../core/locales';
import { createQuestionAnswerKeys } from '../core/questions';

type QuestionCardMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'question-card' }>;

type SelectionState = {
  selectedOptionIndexes: number[];
  otherSelected: boolean;
  otherText: string;
};

const OPTION_LABELS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
const MAX_VISIBLE_OPTIONS = OPTION_LABELS.length - 1;

function initSelections(count: number): SelectionState[] {
  return Array.from({ length: count }, () => ({
    selectedOptionIndexes: [],
    otherSelected: false,
    otherText: '',
  }));
}

function hasQuestionAnswer(question: BuilderQuestion | undefined, selection: SelectionState | undefined) {
  if (!question || !selection) return false;
  return selection.selectedOptionIndexes.length > 0 || (selection.otherSelected && selection.otherText.trim() !== '');
}

function optionLabel(index: number) {
  return OPTION_LABELS[index] ?? '';
}

export function QuestionCard({
  message,
  locale = 'zh-CN',
  isSubmitting = false,
  onSubmit,
}: {
  message: QuestionCardMessage;
  locale?: BuilderPublicSiteLocaleInput;
  isSubmitting?: boolean;
  onSubmit?: (message: QuestionCardMessage, answers: BuilderQuestionAnswers) => void | Promise<void>;
}) {
  const labels = questionCardLabels(locale);
  const questions = message.questions;
  const answerKeys = useMemo(() => createQuestionAnswerKeys(questions), [questions]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selections, setSelections] = useState<SelectionState[]>(() => initSelections(questions.length));
  const [localSubmitting, setLocalSubmitting] = useState(false);
  const lastInteractionRef = useRef<{ questionIndex: number; source: 'option' | 'other' } | null>(null);
  const isComposingRef = useRef(false);
  const submitInFlightRef = useRef(false);

  useEffect(() => {
    setSelections(initSelections(questions.length));
    setCurrentIndex(0);
    setLocalSubmitting(false);
    submitInFlightRef.current = false;
    lastInteractionRef.current = null;
  }, [questions]);

  const buildAnswers = useCallback((skipped: boolean): BuilderQuestionAnswers => {
    const answers: Record<string, BuilderQuestionAnswerEntry> = {};
    questions.forEach((question, index) => {
      const selection = selections[index];
      if (!selection) return;
      const selectedOptions = selection.selectedOptionIndexes
        .map((optionIndex) => question.options[optionIndex]?.label ?? '')
        .filter(Boolean);
      const otherText = selection.otherSelected ? selection.otherText.trim() : '';
      if (selectedOptions.length === 0 && otherText === '') return;
      answers[answerKeys[index]!] = {
        selected_options: selectedOptions,
        other_text: otherText,
      };
    });
    return { answers, skipped };
  }, [answerKeys, questions, selections]);

  const submit = useCallback(async (answers: BuilderQuestionAnswers) => {
    if (!onSubmit || isSubmitting || localSubmitting || submitInFlightRef.current) return;
    submitInFlightRef.current = true;
    setLocalSubmitting(true);
    try {
      await onSubmit(message, answers);
    } catch (error) {
      submitInFlightRef.current = false;
      setLocalSubmitting(false);
      throw error;
    }
  }, [isSubmitting, localSubmitting, message, onSubmit]);

  const handleSelectOption = useCallback((questionIndex: number, optionIndex: number) => {
    lastInteractionRef.current = { questionIndex, source: 'option' };
    setSelections((previous) => previous.map((selection, index) => {
      if (index !== questionIndex) return selection;
      const question = questions[questionIndex];
      if (!question) return selection;
      if (question.multiSelect) {
        const exists = selection.selectedOptionIndexes.includes(optionIndex);
        return {
          ...selection,
          selectedOptionIndexes: exists
            ? selection.selectedOptionIndexes.filter((item) => item !== optionIndex)
            : [...selection.selectedOptionIndexes, optionIndex].sort((a, b) => a - b),
        };
      }
      const alreadySelected = selection.selectedOptionIndexes.includes(optionIndex);
      return {
        ...selection,
        selectedOptionIndexes: alreadySelected ? [] : [optionIndex],
        otherSelected: false,
        otherText: '',
      };
    }));
  }, [questions]);

  const handleToggleOther = useCallback((questionIndex: number) => {
    lastInteractionRef.current = { questionIndex, source: 'other' };
    setSelections((previous) => previous.map((selection, index) => {
      if (index !== questionIndex) return selection;
      const question = questions[questionIndex];
      if (!question) return selection;
      const otherSelected = !selection.otherSelected;
      if (question.multiSelect) {
        return { ...selection, otherSelected, otherText: otherSelected ? selection.otherText : '' };
      }
      return {
        ...selection,
        selectedOptionIndexes: [],
        otherSelected,
        otherText: otherSelected ? selection.otherText : '',
      };
    }));
  }, [questions]);

  const handleChangeOtherText = useCallback((questionIndex: number, value: string) => {
    lastInteractionRef.current = { questionIndex, source: 'other' };
    setSelections((previous) => previous.map((selection, index) => (
      index === questionIndex ? { ...selection, otherSelected: true, otherText: value } : selection
    )));
  }, []);

  const handleContinue = useCallback(async () => {
    if (isSubmitting || localSubmitting) return;
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      return;
    }
    await submit(buildAnswers(false));
  }, [buildAnswers, currentIndex, isSubmitting, localSubmitting, questions.length, submit]);

  const handleSkipRemaining = useCallback(async () => {
    await submit(buildAnswers(true));
  }, [buildAnswers, submit]);

  useEffect(() => {
    const interaction = lastInteractionRef.current;
    if (!interaction || isSubmitting || localSubmitting || questions.length === 0) return;
    lastInteractionRef.current = null;

    const changedQuestion = questions[interaction.questionIndex];
    const answeredCurrent = hasQuestionAnswer(changedQuestion, selections[interaction.questionIndex]);
    const canAutoNext =
      interaction.source === 'option' &&
      changedQuestion &&
      !changedQuestion.multiSelect &&
      answeredCurrent &&
      interaction.questionIndex === currentIndex &&
      currentIndex < questions.length - 1;

    if (canAutoNext) setCurrentIndex(currentIndex + 1);
  }, [currentIndex, isSubmitting, localSubmitting, questions, selections]);

  if (message.status !== 'waiting') return null;

  const currentQuestion = questions[currentIndex];
  const currentSelection = selections[currentIndex];
  if (!currentQuestion) return null;
  const visibleOptions = currentQuestion.options.slice(0, MAX_VISIBLE_OPTIONS);
  const busy = isSubmitting || localSubmitting;

  return (
    <section className="bps-question-card" data-testid={`bps-question-card-${message.toolCallId ?? 'unknown'}`}>
      <div className="bps-question-card-header">
        <span className="bps-question-card-icon"><CircleHelp className="bps-question-card-icon-svg" /></span>
        <span className="bps-question-card-title">{labels.questions}</span>
        <button
          type="button"
          className="bps-question-nav"
          onClick={() => setCurrentIndex(Math.max(currentIndex - 1, 0))}
          disabled={currentIndex === 0 || busy}
          aria-label={labels.previousQuestion}
        >
          <ChevronUp className="bps-question-nav-icon" />
        </button>
        <span className="bps-question-count">{currentIndex + 1}/{questions.length}</span>
        <button
          type="button"
          className="bps-question-nav"
          onClick={() => setCurrentIndex(Math.min(currentIndex + 1, questions.length - 1))}
          disabled={currentIndex === questions.length - 1 || busy}
          aria-label={labels.nextQuestion}
        >
          <ChevronDown className="bps-question-nav-icon" />
        </button>
      </div>

      <div className="bps-question-card-body">
        <div className="bps-question-prompt">
          <span className="bps-question-number">{currentIndex + 1}.</span>
          <span className="bps-question-text">{currentQuestion.question}</span>
        </div>

        <div className="bps-question-options">
          {visibleOptions.map((option, optionIndex) => {
            const selected = Boolean(currentSelection?.selectedOptionIndexes.includes(optionIndex));
            return (
              <button
                key={`${option.label}-${optionIndex}`}
                type="button"
                className={`bps-question-option ${selected ? 'is-selected' : ''}`}
                onClick={() => handleSelectOption(currentIndex, optionIndex)}
                disabled={busy}
              >
                <span className="bps-question-option-key">{optionLabel(optionIndex)}</span>
                <span className="bps-question-option-label">{option.label}</span>
              </button>
            );
          })}

          <div className="bps-question-other">
            <button
              type="button"
              className={`bps-question-option-key bps-question-other-toggle ${currentSelection?.otherSelected ? 'is-selected' : ''}`}
              onClick={() => handleToggleOther(currentIndex)}
              disabled={busy}
              aria-label={labels.otherOption}
            >
              {optionLabel(visibleOptions.length)}
            </button>
            <input
              className="bps-question-other-input"
              value={currentSelection?.otherText ?? ''}
              placeholder={labels.otherPlaceholder}
              disabled={busy}
              onFocus={() => {
                if (!currentSelection?.otherSelected) handleToggleOther(currentIndex);
              }}
              onChange={(event) => handleChangeOtherText(currentIndex, event.target.value)}
              onCompositionStart={() => {
                isComposingRef.current = true;
              }}
              onCompositionEnd={() => {
                isComposingRef.current = false;
              }}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !isComposingRef.current && !event.nativeEvent.isComposing) {
                  event.preventDefault();
                  void handleContinue().catch(() => undefined);
                }
              }}
            />
          </div>
        </div>
      </div>

      <div className="bps-question-card-footer">
        <button
          type="button"
          className="bps-question-secondary"
          onClick={() => void handleSkipRemaining().catch(() => undefined)}
          disabled={busy}
        >
          {busy ? labels.submitting : labels.skipRemaining}
        </button>
        <button
          type="button"
          className="bps-question-primary"
          onClick={() => void handleContinue().catch(() => undefined)}
          disabled={busy}
        >
          {busy ? labels.submitting : labels.continue}
        </button>
      </div>
    </section>
  );
}
