from robot.api.deco import keyword
import datetime
from Browser import Browser
import faker
from robot.libraries.BuiltIn import BuiltIn

class NS_Common_Keywords(object):

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"
    ROBOT_EXIT_ON_FAILURE = True

    def __init__(self):
        self.builtin = BuiltIn()

    @keyword('Selecteer Waarde In Combobox')
    def selecteer_waarde_in_combobox(self, xpath, value):
        browser_lib = self.builtin.get_library_instance('Browser')
        browser_lib.click(xpath)
        browser_lib.type_text(xpath, value, delay=0.01)
        browser_lib.press_keys(xpath, 'Enter')

    @keyword('Selecteer Waarde In Multiselect Combobox')
    def selecteer_waarde_in_multiselect_combobox(self, xpath, value):
        browser_lib = self.builtin.get_library_instance('Browser')
        browser_lib.click(xpath)
        browser_lib.sleep(0.1)
        browser_lib.type_text(xpath, value)
        browser_lib.sleep(0.1)
        browser_lib.press_keys(xpath, 'ArrowDown')
        browser_lib.sleep(0.1)
        browser_lib.press_keys(xpath, 'Enter')
        browser_lib.sleep(0.1)
        browser_lib.press_keys(xpath, 'Tab')
        browser_lib.press_keys(xpath, 'Tab')

    @keyword('Get Modal Container')
    def get_modal_container(self, title):
        browser_lib = self.builtin.get_library_instance('Browser')
        xpath = f'//h4[contains(text(),"{title}")]/ancestor::div[contains(@class, "modal-dialog")]'
        return browser_lib.get_element(xpath)

    @keyword('Close Modal')
    def close_modal(self, title, action):
        browser_lib = self.builtin.get_library_instance('Browser')
        container = self.get_modal_container(title)
        browser_lib.click(f'{container}//button[text()="{action}"]')
        self.wacht_tot_element_onzichtbaar_is(container)

    @keyword('Wait For Modal')
    def wait_for_modal(self, title):
        browser_lib = self.builtin.get_library_instance('Browser')
        xpath = f'//h4[contains(text(),"{title}")]/ancestor::div[contains(@class, "modal-dialog")]'
        browser_lib.wait_for_elements_state(xpath, 'visible')

    @keyword('Dismiss Modal')
    def dismiss_modal(self, title):
        self.close_modal(title, '.modal-header > .close')

    @keyword('Pas Format Aan Van Datum')
    def pas_format_aan_van_datum(self, datum, input_format='%d-%m-%Y', output_format='%Y-%m-%d'):
        return datetime.datetime.strptime(datum, input_format).strftime(output_format)

    @keyword('Bepaal Huidige Datum')
    def bepaal_huidige_datum(self, format='%d-%m-%Y'):
        return datetime.datetime.now().strftime(format)

    @keyword('Bepaal Datum Plus Extra Dagen')
    def bepaal_datum_plus_extra_dagen(self, aantal_dagen, begin_datum=None, format='%d-%m-%Y'):
        if begin_datum:
            start = datetime.datetime.strptime(begin_datum, format)
        else:
            start = datetime.datetime.now()
        nieuwe_datum = start + datetime.timedelta(days=int(aantal_dagen))
        return nieuwe_datum.strftime(format)

    @keyword('Creeer Willekeurige Zin')
    def creeer_willekeurige_zin(self):
        fake = faker.Faker('nl_NL')
        return fake.sentence(nb_words=8)

    @keyword('Creeer Willekeurig Woord')
    def creeer_willekeurig_woord(self):
        fake = faker.Faker('nl_NL')
        return fake.word()

    @keyword('Wacht Tot Element Onzichtbaar Is')
    def wacht_tot_element_onzichtbaar_is(self, xpath):
        browser_lib = self.builtin.get_library_instance('Browser')
        count = browser_lib.get_element_count(xpath)
        tries = 0
        while count and tries < 100:
            browser_lib.sleep(0.05)
            count = browser_lib.get_element_count(xpath)
            tries += 1

    @keyword('Wacht Op Laden Element')
    def wacht_op_laden_element(self, xpath, eindstatus='visible', wachttijd='10s'):
        from robot.api import logger
        browser_lib = self.builtin.get_library_instance('Browser')

        # Log of de functie beschikbaar is
        if hasattr(browser_lib, 'wait_for_elements_state'):
            logger.info("✅ Functie 'wait_for_elements_state' is beschikbaar in de Browser library.")
        else:
            logger.warn("❌ Functie 'wait_for_elements_state' is NIET beschikbaar in de Browser library!")
            raise AttributeError("De functie 'wait_for_elements_state' bestaat niet in de Browser library. Is de juiste versie geïnstalleerd?")

        logger.info(f"Type selector: {type(xpath)} | waarde: {xpath}")
        logger.info(f"Type eindstatus: {type(eindstatus)} | waarde: {eindstatus}")
        logger.info(f"Type wachttijd: {type(wachttijd)} | waarde: {wachttijd}")

        # Probeer de Browser library state enums te gebruiken
        try:
            from Browser import ElementState
            state_mapping = {
                'attached': ElementState.attached,
                'detached': ElementState.detached,
                'visible': ElementState.visible,
                'hidden': ElementState.hidden,
                'enabled': ElementState.enabled,
                'disabled': ElementState.disabled,
                'editable': ElementState.editable
            }
        except ImportError:
            # Fallback naar string waarden
            logger.info("ElementState enum niet beschikbaar, gebruik string waarden")
            state_mapping = {
                'attached': 'attached',
                'detached': 'detached',
                'visible': 'visible',
                'hidden': 'hidden',
                'enabled': 'enabled',
                'disabled': 'disabled',
                'editable': 'editable'
            }

        if eindstatus not in state_mapping:
            geldige_statussen = list(state_mapping.keys())
            raise ValueError(f"'{eindstatus}' is geen geldige eindstatus. Kies uit: {', '.join(geldige_statussen)}")

        # Gebruik de juiste state parameter
        try:
            browser_lib.wait_for_elements_state(xpath, state=state_mapping[eindstatus], timeout=wachttijd)
            logger.info(f"✅ Element met selector '{xpath}' heeft de gewenste status '{eindstatus}' bereikt.")
        except Exception as e:
            logger.error(f"❌ Fout bij wachten op element: {str(e)}")
            raise

    @keyword('Wacht Op Het Laden Van Een Tabel')
    def wacht_op_het_laden_van_een_tabel(self, xpath):
        browser_lib = self.builtin.get_library_instance('Browser')
        aantal = 0
        tries = 0
        while not aantal and tries < 10:
            browser_lib.sleep(0.05)
            aantal = browser_lib.get_element_count(f'{xpath}//div[@class="paging-status"]')
            tries += 1

    @keyword('Tel Aantal Regels Van Tabel')
    def tel_aantal_regels_van_tabel(self, xpath):
        browser_lib = self.builtin.get_library_instance('Browser')
        return browser_lib.get_element_count(f'{xpath}//div[@role="row"]')

    @keyword('Wacht Op Herladen Data Tabel')
    def wacht_op_herladen_data_tabel(self, xpath, aantal_regels):
        browser_lib = self.builtin.get_library_instance('Browser')
        nieuw_aantal = aantal_regels
        tries = 0
        while nieuw_aantal == aantal_regels and tries < 20:
            browser_lib.sleep(0.05)
            nieuw_aantal = self.tel_aantal_regels_van_tabel(xpath)
            tries += 1

    @keyword('Formatteer Bedrag')
    def formatteer_bedrag(self, amount):
        return '{:,.2f}'.format(float(amount)).replace(',', 'X').replace('.', ',').replace('X', '.')
