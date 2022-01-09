#main modules
import asyncio
import time
import discord
import clashroyale
from redbot.core import commands
from discord_components import DiscordComponents, Button

#webdriver modules
from selenium.webdriver import Chrome,Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.firefox.options import Options
from webdriver_manager.chrome import ChromeDriverManager

#webdriver error handler modules
from selenium.common.exceptions import NoSuchElementException 
from urllib3.exceptions import MaxRetryError

#image/pdf modules
from PIL import Image, ImageDraw, ImageFont

#webpage data extractor module
from bs4 import BeautifulSoup as bs

#other modules
from fake_useragent import UserAgent
import pickle


LOG_CHANNEL_GUILD_ID = 875615868166475776
LOG_CHANNEL_ID = 878968502365618186

class Analyzer(commands.Cog):
    """Credits: Gladiator#2979"""

    def __init__(self, bot):
        self.bot = bot
        self.all_decks = []
        for guild in self.bot.guilds:
            if guild.id == LOG_CHANNEL_GUILD_ID:
                self.logchannel = guild.get_channel(LOG_CHANNEL_ID)
        DiscordComponents(self.bot)
        

    def set_up_browser(self):
        userAgent = UserAgent().random
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument("--enable-javascript")
        # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # chrome_options.add_argument(f'user-agent={userAgent}')
        # chrome_options.add_argument('window-size=1200x600')
        # chrome_options.add_argument("start-maximized")
        # self.driver = Chrome(ChromeDriverManager().install(), options=chrome_options)
        firefox_options = Options()
        #firefox_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #firefox_options.add_experimental_option('useAutomationExtension', False)
        firefox_options.add_argument("--headless")
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument("--enable-javascript")
        firefox_options.add_argument('--disable-blink-features=AutomationControlled')
        firefox_options.add_argument(f'user-agent={userAgent}')
        firefox_options.add_argument('window-size=1200x600')
        firefox_options.add_argument("start-maximized")
        firefox_options.add_argument("user-data-dir=selenium")
        self.driver = Chrome(ChromeDriverManager(version='96.0.4664.45').install(),options=firefox_options)

    
    async def login(self, url: str):
        try:
         creds = await self.bot.get_shared_api_tokens('tw_credentials')
         USERuser = creds['un']
         USERpassword = creds['pw']
        except AttributeError:
            return await self.logchannel.send("Please set your twitter credentials.")
        self.driver.get(url=url)
        time.sleep(2)
        try:
         email = self.driver.find_element_by_xpath('//*[@id="username_or_email"]') #find_element_by_id('username_or_email')
         password = self.driver.find_element_by_xpath('//*[@id="password"]') #find_element_by_id('password')
         login_button = self.driver.find_element_by_xpath('//*[@id="allow"]')#find_element_by_id('allow')
         email.send_keys(USERuser)
         password.send_keys(USERpassword)
         login_button.send_keys(Keys.ENTER)
         try:
          re = self.driver.find_element_by_id('challenge_response')
          re.send_keys(USERuser)
          bt1 = self.driver.find_element_by_id('email_challenge_submit')
          bt1.send_keys(Keys.ENTER)
          time.sleep(3)
         except NoSuchElementException:
             pass
        except NoSuchElementException as e:
            pass
        except Exception as e:
            await self.logchannel.send(e)

        try:
          auth_button = self.driver.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]') #//*[@id="allow"]
          auth_button.send_keys(Keys.ENTER)
          time.sleep(3)
        except NoSuchElementException as e:
            pass
        try:
            self.driver.find_element_by_id('allow').click()
        except:
            pass
        except Exception as e:
            await self.logchannel.send(e)

    async def login_again(self):
        try:
         creds = await self.bot.get_shared_api_tokens('tw_credentials')
         USERuser = creds['un']
         USERpassword = creds['pw']
        except AttributeError:
            return await self.logchannel.send("Please set your twitter credentials.")
        try:
         email = self.driver.find_element_by_id('username_or_email')
         password = self.driver.find_element_by_id('session[password]')
         login_button = self.driver.find_element_by_id('allow')
         email.send_keys('CRIndiaBot')
         password.send_keys(USERpassword)
         login_button.send_keys(Keys.ENTER)
         time.sleep(2)
         try:
          re = self.driver.find_element_by_id('challenge_response')
          re.send_keys(USERuser)
          bt1 = self.driver.find_element_by_id('email_challenge_submit')
          bt1.send_keys(Keys.ENTER)
         except NoSuchElementException:
             pass
        except NoSuchElementException as e:
             pass
        except Exception as e:
            await self.logchannel.send(e)
        time.sleep(2)
        try:
          auth_button = self.driver.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]') #//*[@id="allow"]
          auth_button.send_keys(Keys.ENTER)
          time.sleep(1)
        except NoSuchElementException as e:
            pass
        except Exception as e:
            await self.logchannel.send(e)


    async def getBattleID(self, ctx):
                                  
        self.msG = await ctx.send(content=f"{ctx.author.mention}, Please choose which category to analyze:", components=[[Button(style=2, label="Ladder")],[Button(style=2, label="GC")],[Button(style=2, label="Friendly")],[Button(style=2, label="Clan 1v1")],[Button(style=2, label="Clan 2v2")]])
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:

            click = await self.bot.wait_for('button_click', timeout=30, check=check)
            battleType = click.component.label
            self.battletype = battleType
            self.CC = click
            await click.message.edit(content=f"{ctx.author.mention}, Analyzer is fetching data...",components=[])
            try:
             await click.respond()
            except:
                pass

            if battleType.lower() == 'gc':
                return 'challenge-grand'
            elif battleType.lower() == 'classic challenge':
                return 'challenge-classic'
            elif battleType.lower() == 'ladder':
                return 'PvP'
            elif battleType.lower() == 'clan 1v1':
                return 'clanMate'
            elif battleType.lower() == 'clan 2v2':
                    return 'clanMate2v2'
            elif battleType.lower() == 'friendly':
                return 'friendly'
            elif battleType.lower() == 'global tournament':
                return 'global-tournament'    
        except TimeoutError:
            await ctx.send("TIMEOUT.",components=[])
            return ''
        except Exception as e:
            await self.logchannel.send(e)

    def clear_old_cache(self):
        self.all_decks.clear()
        self.counter = 1
        self.pages = 0
        self.decks = 0
        self.text = ''
        self.battletype = ''
        self.tag = ''


    def verifyTag(self, tag):
        """Check if a player's tag is valid"""
        check = ["P", "Y", "L", "Q", "G", "R", "J", "C", "U", "V", "0", "2", "8", "9"]
        if len(tag) > 15:
            return False
        if any(i not in check for i in tag):
            return False
        return True

    def formatTag(self, tag):
        """Sanitize and format CR Tag"""
        return tag.strip("#").upper().replace("O", "0")    
    
    async def yesORno(self, ctx):
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        msG = await ctx.send(content="Do you want a pdf of the images?",components=[[Button(style=3, label="Yes")],[Button(style=4, label="No")]])
        try:
         click = await self.bot.wait_for('button_click', timeout=60, check=check)
         await msG.delete()
         if click.component.label.lower() == 'yes':
             try:
              await click.respond()
             except:
              pass
             await asyncio.sleep(1)
             return True
         else:
             try:
              await click.respond()
             except:
              pass
             await asyncio.sleep(1)
             #
             return False
        except TimeoutError:
            return False

    async def getName(self, tag: str):
     token = await self.bot.get_shared_api_tokens('crapi')
     token = token['api_key']
     self.clash = clashroyale.official_api.Client(token, is_async=True)
     try:
      player = await self.clash.get_player(tag)
      name = player.name
      return name
     except Exception as e:
      return ''

    async def pagesORdecks(self, ctx):
        components = [ [Button(style=2, label="Collection")], [Button(style=2, label='Specific')] ]
        msG = await ctx.send("```Please choose any one option.\n\n\u21A3 Specific - If you want to get a fixed number of decks in the output.\n\u21A3 Collection - Has around 10 decks per 1 collection```",components=components)
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        try:
            click = await self.bot.wait_for('button_click', timeout=15, check=check)
            response = click.component.label
            if response == 'Collection':
                await ctx.send(content= 'Please enter the number of collections.',components=[])
                try:
                 await click.respond()
                except:
                 pass
                await asyncio.sleep(1)
                #
                msg = await self.bot.wait_for('message', timeout = 60, check=check)
                input = msg.content
                try:
                    self.pages = int(input)
                except ValueError:
                    await click.respond(content="Invalid Value.",ephemeral=False)
                    return #
            elif response == 'Specific':
                await ctx.send(content= 'Please enter the number of decks.',components=[])
                try:
                 await click.respond()
                except:
                 pass
                await asyncio.sleep(1)
                #
                msg = await self.bot.wait_for('message', timeout = 60, check=check)
                input = msg.content
                try:
                    self.decks = int(input)
                except ValueError:

                    await click.respond(content="Invalid Value.",ephemeral=False)
                    await asyncio.sleep(1)
                    return #
        except TimeoutError:
            try:
             await click.respond()
            except:
                pass
            await ctx.send("TIMEOUT")


    async def image(self, ctx, url:str, count: int):
        deck = self.bot.get_cog("Deck")
        await deck.only_deck_image(ctx, url, count)

    async def pdf(self, ctx, url:str, count: int):
        deck = self.bot.get_cog("Deck")
        return await deck.only_deck_pdf(ctx, url, count)


    async def getData(self, ctx, html:str):         
        counter = 2
        s = bs(html)
        listX = s.find_all('a', class_='button_popup item', href = True)
        for deck in listX:
            if counter%2==0:
             counter = counter+1
             url = deck['href']
             self.all_decks.append(url)
            else:
             counter = counter+1

        if len(self.all_decks) == 0:
            self.driver.get_screenshot_as_file('noDATA.png')
            await self.logchannel.send(file=discord.File('noDATA.png'))
            embed = discord.Embed()
            embed.add_field(name='\u200b', value=f"Sorry, analyzer couldn't fetch data for this user.\n[Click Here]({self.driver.current_url}) to be redirected to player profile.")
            return await ctx.send(embed=embed)
            # try:
            #     await self.login(url = self.driver.current_url)
            #     await self.getData(ctx,self.driver.current_url)
            # except Exception as exceptioN:
            #     await self.logchannel.send(exceptioN)

            

        if self.counter != 0:
         if self.counter == self.pages:
             answer = await self.yesORno(ctx)
             if not answer:
               all_decks_without_repetition = set(self.all_decks)
               for i in all_decks_without_repetition:
                    count = self.all_decks.count(str(i))
                    await self.image(ctx, i, count)
             else:
                  list_of_files = []
                  list_of_images = []
                  all_decks_without_repetition = set(self.all_decks)
                  for i in all_decks_without_repetition:
                    count = self.all_decks.count(str(i))
                    fileName = await self.pdf(ctx, i, count)
                    list_of_files.append(fileName)
                  for i in range(0, len(list_of_files)):
                      img = Image.open(list_of_files[i])
                      list_of_images.append(img.convert('RGB'))
                  im = Image.new("RGB",(Image.open(list_of_files[0]).size),(35,39,42))
                  ign = await self.getName(self.tag)
                  msg = f'{self.text.upper()}{ign}'
                  msg1 = '~ bot by Gladiator#2979'
                  msg2 = f'* {self.tag} ~ {self.battletype.upper()}'
                  draw = ImageDraw.Draw(im)
                  draw1 = ImageDraw.Draw(im)
                  myFont = ImageFont.truetype("/root/clanbot/cogs/CogManager/cogs/deck/data/fonts/Supercell-magic-webfont.ttf", 50)
                  font = ImageFont.truetype("/root/clanbot/cogs/CogManager/cogs/deck/data/fonts/Supercell-magic-webfont.ttf", 15)
                  draw.text((5,0),msg,int('FFFFFF',16),myFont,align='center')

                  ascent, descent = myFont.getmetrics()

                  text_width = myFont.getmask(msg).getbbox()[2]
                  text_height = myFont.getmask(msg).getbbox()[3] + descent


                  draw1.text((text_width-250,text_height+160),msg1,int('FFFFFF',16),font,align='right',size=8)
                  draw1.text((5,text_height+160),msg2,int('FFFFFF',16),font,align='center',size=8)


                  im.save(f'a-{ign}.pdf',save_all=True, append_images=list_of_images)
                  await ctx.send(file=discord.File(f'a-{ign}.pdf'))  
             return

         elif self.counter == self.decks:
             answer = await self.yesORno(ctx)
             if not answer:
              decks = []
              for N in range(0, self.decks):
                  decks.append(self.all_decks[N])
              all_decks_no_repetition = set(decks)
              for i in all_decks_no_repetition:
                    count = decks.count(str(i))
                    await self.image(ctx, i, count)
             else:
                  decks = []
                  list_of_files = []
                  list_of_images = []
                  for N in range(0, self.decks):
                   decks.append(self.all_decks[N])
                  all_decks_no_repetition = set(decks)
                  for i in all_decks_no_repetition:
                    count = decks.count(str(i))
                    fileName = await self.pdf(ctx, i, count)
                    list_of_files.append(fileName)

                  for i in range(0, len(list_of_files)):
                      img = Image.open(list_of_files[i])
                      list_of_images.append(img.convert('RGB'))
                  im = Image.new("RGB",(Image.open(list_of_files[0]).size),(35,39,42))
                  ign = await self.getName(self.tag)
                  msg = f'{self.text.upper()}{ign}'
                  msg1 = '~ bot by Gladiator#2979'
                  msg2 = f'* {self.tag} ~ {self.battletype.upper()}'
                  draw = ImageDraw.Draw(im)
                  draw1 = ImageDraw.Draw(im)
                  myFont = ImageFont.truetype("/root/clanbot/cogs/CogManager/cogs/deck/data/fonts/Supercell-magic-webfont.ttf", 50)
                  font = ImageFont.truetype("/root/clanbot/cogs/CogManager/cogs/deck/data/fonts/Supercell-magic-webfont.ttf", 15)
                  draw.text((5,0),msg,int('FFFFFF',16),myFont,align='center')

                  ascent, descent = myFont.getmetrics()

                  text_width = myFont.getmask(msg).getbbox()[2]
                  text_height = myFont.getmask(msg).getbbox()[3] + descent


                  draw1.text((text_width-300,text_height+160),msg1,int('FFFFFF',16),font,align='right',size=8)
                  draw1.text((5,text_height+160),msg2,int('FFFFFF',16),font,align='center',size=8)


                  im.save(f'a-{ign}.pdf',save_all=True, append_images=list_of_images)
                  await ctx.send(file=discord.File(f'a-{ign}.pdf'))                 
             return

        self.counter = self.counter + 1            
        try:
            if self.pages != 0:
             percent = (self.counter/self.pages*100)
             if percent > 100.0:
                 percent = 100.0
             await self.message.edit(content = f"Analyzer's current progress: {int(percent)}%")
            elif self.decks != 0:
             percent = (self.counter/self.decks*100)
             if percent > 100.0:
                 percent = 100.0
             await self.message.edit(content = f"Analyzer's current progress: {int(percent)}%")
            time.sleep(2)
            nextButton = self.driver.find_element_by_xpath('//*[@id="page_content"]/div[7]/div/a[3]')
            time.sleep(2)

            nextButton.send_keys(Keys.ENTER)
            try:
                await self.getData(ctx, self.driver.page_source)
            except Exception as e:
                await self.logchannel.send(e)
        except NoSuchElementException as ex:

             self.driver.get_screenshot_as_file('noDATA.png')
             await self.logchannel.send(file=discord.File('noDATA.png'))
             await self.logchannel.send(ex)
        except Exception as excep:
            await self.logchannel.send(excep)
    

    @commands.command()
    async def analyze(self, ctx, tag: str):
        self.clear_old_cache()

        self.text = 'Analyzer: '
        tag = self.formatTag(tag=tag)
        if self.verifyTag(tag=tag) is False:
            return await ctx.send("Invalid tag")
        self.tag = tag
        bID = await self.getBattleID(ctx)
        self.battleID = bID
        if bID == '':
            return
        else:

            try:
              self.driver.get(url=f'https://royaleapi.com/login/twitter?r=/player/{tag}/battles/history?battle_type={bID}')
              self.continue_to_site()
              await self.pagesORdecks(ctx) 
              if self.pages != 0:
                self.message = await ctx.send(content = f"Analyzer's current progress: {str((self.counter/self.pages*100))}%")
                await self.getData(ctx,html=self.driver.page_source)
              elif self.decks != 0:
                self.message = await ctx.send(content = f"Analyzer's current progress: {str((self.counter/self.decks*100))}%")
                await self.getData(ctx,html=self.driver.page_source)
              else:
                  return await ctx.send("No input.")

              history = await ctx.channel.history(limit=20).flatten()
              for message in history:
                  try:
                   if message.author.id == 761173493009088553:
                      if len(message.attachments) == 0:
                          await message.delete()
                  except Exception:
                      continue
              
            except AttributeError:
                self.__init__(self.bot)
                self.set_up_browser()
                self.driver.get(url=f'https://royaleapi.com/login/twitter?r=/player/{tag}/battles/history?battle_type={bID}')
                self.continue_to_site()
                await self.pagesORdecks(ctx) 
                if self.pages != 0:
                 self.message = await ctx.send(content = f"Analyzer's current progress: {str((self.counter/self.pages*100))}%")
                 await self.getData(ctx,html=self.driver.page_source)
                elif self.decks != 0:
                 self.message = await ctx.send(content = f"Analyzer's current progress: {str((self.counter/self.decks*100))}%")
                 await self.getData(ctx,html=self.driver.page_source)
                else:
                 return await ctx.send("No input.")
            except Exception as e:
                await self.logchannel.send(e)
                await ctx.send("Unknown error occured. Please try again.")

            
    def continue_to_site(self):
        try:
            self.driver.find_element_by_xpath('//*[@id="tyche_cmp_modal"]/div/div/div/div[5]/div[2]/a').click()
        except:
            pass
        try:
            self.driver.find_element_by_xpath('//*[@id="tyche_cmp_modal"]/div/div/div/div[5]/div[2]/a/span').click()
        except:
            pass