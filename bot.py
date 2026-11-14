import os, random, asyncio
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = discord.Object(id=int(os.getenv("GUILD_ID")))

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)


class SorteioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participantes = set()

    @discord.ui.button(label="Participar 🎉", style=discord.ButtonStyle.success)
    async def participar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participantes:
            await interaction.response.send_message("Já estás a participar! ✅", ephemeral=True)
            return
        self.participantes.add(interaction.user.id)
        await interaction.response.send_message("Estás dentro! Boa sorte 🍀", ephemeral=True)


@tree.command(name="sorteio", description="Cria um sorteio", guild=GUILD)
@app_commands.describe(premio="O que vais sortear", minutos="Duração em minutos", vencedores="Número de vencedores")
async def sorteio(
    interaction: discord.Interaction,
    premio: str,
    minutos: app_commands.Range[int, 1, 1440],
    vencedores: app_commands.Range[int, 1, 10] = 1,
):
    view = SorteioView()
    embed = discord.Embed(
        title=f"🎁 Sorteio: {premio}",
        description=f"Carrega no botão para participar!\nTermina em **{minutos} min**.\nVencedores: **{vencedores}**",
        color=0x2F9188,
    )
    await interaction.response.send_message("Sorteio criado! ✅", ephemeral=True)
    mensagem = await interaction.channel.send(embed=embed, view=view)

    await asyncio.sleep(minutos * 60)

    view.participar.disabled = True
    await mensagem.edit(view=view)

    participantes = list(view.participantes)
    if not participantes:
        await interaction.channel.send(f"O sorteio **{premio}** terminou, mas ninguém participou 😢")
        return
    escolhidos = random.sample(participantes, min(vencedores, len(participantes)))
    mencoes = ", ".join(f"<@{u}>" for u in escolhidos)
    await interaction.channel.send(f"🎉 Parabéns {mencoes}! Ganharam **{premio}**!")


@client.event
async def on_ready():
    await tree.sync(guild=GUILD)
    print(f"Ligado como {client.user}")


client.run(TOKEN)