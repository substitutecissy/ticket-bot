def temporary:
    print('Navigate to the event page please. Waiting for 10 seconds...')
    print('Trying to buy ticket...')
    # click buy ticket
    buy_btn = find_element_with_retry(By.ID, 'btn_concert_ticket')
    buy_btn.click()

    # close the modal
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'dialogIFrame')))
    close_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ui-button-text-only')))
    sleep(1)
    close_btn.click()

    # click NEXT
    next_btn = find_element_with_retry(By.CLASS_NAME, 'btn_next_b_on');
    next_btn.click()

    # wait for user to select seats
    print("Select seats and hit the NEXT button in the web browser.")
    
    # select 2 tickets from dropdown
    wait.until(EC.element_to_be_clickable((By.ID, 'selPromotion0')))
    wait.until(EC.element_to_be_clickable((By.ID, 'imgStepCtrlBtn03_next')))
    dropdown_btn = find_element_with_retry(By.ID, 'selPromotion0')
    select = Select(dropdown_btn)
    select.select_by_visible_text('2매')
    next_btn = find_element_with_retry(By.ID, 'imgStepCtrlBtn03_next')
    next_btn.click()

    # click next button
    try:
        next_btn = wait.until(EC.element_to_be_clickable((By.ID, 'imgStepCtrlBtn04_next')))
        next_btn = find_element_with_retry(By.ID, 'imgStepCtrlBtn04_next')
        next_btn.click()
    except ElementClickInterceptedException:
        print("Trying to click on the NEXT button again...")
        driver.execute_script("arguments[0].click()", next_btn)
    

    # agree to terms and conditions
    terms = wait.until(EC.element_to_be_clickable((By.ID, 'cbxCancelFeeAgree')))
    sleep(1)
    terms.click()
    next_btn = find_element_with_retry(By.ID, 'imgStepCtrlBtn05_pay')
    next_btn.click()
end