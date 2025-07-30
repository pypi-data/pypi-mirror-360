from __future__ import annotations

import json

from typing import Any

from .core import TraderNetCore


class TraderNetSID(TraderNetCore):
    """
    Special client methods requiring login-password authorization excepting
    websockets-related.
    """
    def change_phone(self, phone: str) -> dict[str, Any]:
        """
        Changing a phone number.

        Parameters
        ----------
        phone : str
            A phone number.

        Returns
        -------
        dict[str, Any]
            A dictionary with the following keys: 'phoneId'.

        Notes
        -----
        https://tradernet.ru/tradernet-api/check-phone
        """
        if not self._session_id:
            self.get_authorized()

        return self.plain_request(
            'checkPhone',
            {'phone': phone}
        )

    def check_sms(self, phone_id: int, code: str) -> dict[str, Any]:
        """
        Method for checking the validity of the code sent in SMS using the
        method checkPhone.

        Parameters
        ----------
        phone_id : int
            A phone ID.
        code : str
            A SMS code.

        Returns
        -------
        dict[str, Any]
            A dictionary with the following keys: 'success'.

        Notes
        -----
        https://tradernet.ru/tradernet-api/check-phone
        """
        if not self._session_id:
            self.get_authorized()

        return self.plain_request(
            'checkSms',
            {'phoneId': phone_id, 'code': code}
        )

    def get_tariffs_list(self) -> dict[str, Any]:
        """
        Get a list of available tariffs.

        Returns
        -------
        dict[str, Any]
            Tariffs list.

        Notes
        -----
        https://tradernet.ru/tradernet-api/get-list-tariff
        """
        if not self._session_id:
            self.get_authorized()

        return self.plain_request('GetListTariffs')

    def select_tariff(self, tariff_id: int) -> dict[str, Any]:
        """
        Selecting a tariff.

        Parameters
        ----------
        tariff_id : int
            A tariff ID.

        Returns
        -------
        dict[str, Any]
            A dictionary with the following keys: 'added'.

        Notes
        -----
        https://tradernet.ru/tradernet-api/select-tariff
        """
        if not self._session_id:
            self.get_authorized()

        return self.plain_request(
            'selectTariff',
            {'tariff_id': tariff_id}
        )

    def get_agreement(self) -> bytes:
        """
        Receiving application for joining in PDF format.

        Notes
        -----
        https://tradernet.ru/tradernet-api/get-agreement-pdf
        """
        if not self._session_id:
            self.get_authorized()

        message: dict[str, Any] = {
            'cmd': 'getAgreementPdf',
            'SID': self._session_id
        }
        url = f'{self.url}/api'
        query = {'q': json.dumps(message)}

        response = self.request('get', url, params=query)
        return response.content

    def sign_application(self) -> dict[str, Any]:
        """
        Signing the application by SMS sent to the phone specified by the new
        user.

        Notes
        -----
        https://tradernet.ru/tradernet-api/sign-anketa-electronically
        """
        if not self._session_id:
            self.get_authorized()

        return self.plain_request('signAnketaElectronically')

    def verify_application_signature(
        self,
        phone_id: str,
        code: str
    ) -> dict[str, Any]:
        """
        Confirming the signature via SMS, received to the client's phone number
        using the method `sign_application`.

        Parameters
        ----------
        phone_id : str
            A phone ID.
        code : str
            A SMS code.

        Notes
        -----
        https://tradernet.ru/tradernet-api/check-anketa-electronically-sign-sms-code
        """
        if not self._session_id:
            self.get_authorized()

        return self.plain_request(
            'checkAnketaElectronicallySignSmsCode',
            {'phoneId': phone_id, 'code': code}
        )
