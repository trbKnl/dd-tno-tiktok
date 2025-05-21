import { Weak } from '../../../../helpers'
import { ReactFactoryContext } from '../../factory'
import { PropsUIPromptConfirm } from '../../../../types/prompts'
import { Translator } from '../../../../translator'
import { BodyLarge } from '../elements/text'
import { PrimaryButton } from '../elements/button'
import { JSX } from 'react'
import React from 'react'

type Props = Weak<PropsUIPromptConfirm> & ReactFactoryContext

export const Confirm = (props: Props): JSX.Element => {
  const { resolve } = props
  const { text, ok, cancel } = prepareCopy(props)

  function handleOk (): void {
    resolve?.({ __type__: 'PayloadTrue', value: true })
  }

  return (
    <>
      <BodyLarge text={text} margin='mb-4' />
      <div className='flex flex-row gap-4'>
        <PrimaryButton label={ok} onClick={handleOk} color='text-grey1 bg-tertiary' />
      </div>
    </>
  )
}

interface Copy {
  text: string
  ok: string
  cancel: string
}

function prepareCopy ({ text, ok, cancel, locale }: Props): Copy {
  return {
    text: Translator.translate(text, locale),
    ok: Translator.translate(ok, locale),
    cancel: Translator.translate(cancel, locale)
  }
}
