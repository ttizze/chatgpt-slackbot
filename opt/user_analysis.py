from util import getHistoryIdentifier, getUserIdentifier
import datetime
import openai
import os

from dotenv import load_dotenv
load_dotenv()


def sayUserAnalysis(client, message, say, usingUser, targetUser):
    """
    ユーザー分析のメッセージを送信する
    """

    print(f"<@{usingUser}> さんの依頼で {targetUser} さんについて、直近のパブリックチャンネルの発言より分析します。")
    say(f"<@{usingUser}> さんの依頼で {targetUser} さんについて、直近のパブリックチャンネルの発言より分析します。")

    searchResponse = client.search_messages(token=os.getenv("SLACK_USER_TOKEN"),
                                            query=f"from:{targetUser}", count=100, highlight=False)
    matches = searchResponse["messages"]["matches"]

    if len(matches) == 0:
        say(f"{targetUser} さんの発言は見つかりませんでした。")
        return

    prompt = "以下のSlack上の投稿情報からこのユーザーがどのような人物なのか、どのような性格なのか分析して教えてください。\n\n----------------\n\n"
    for match in matches:
        if match["channel"]["is_private"] == False and match["channel"]["is_mpim"] == False:
            formatedMessage = f"""
投稿チャンネル: {match["channel"]["name"]}
投稿日時: {datetime.datetime.fromtimestamp(float(match["ts"]))}
ユーザー名: {match["username"]}
投稿内容: {match["text"]}
            """

            # 指定文字以上になったら履歴は追加しない 上限は4096トークンだが計算できないので適当な値
            if len(prompt) + len(formatedMessage) < 3800:
                prompt += formatedMessage

    usingTeam = message["team"]
    userIdentifier = getUserIdentifier(usingTeam, usingUser)

    # ChatCompletionを呼び出す
    print(f"prompt: `{prompt}`")
    chatGPTResponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        top_p=1,
        n=1,
        max_tokens=1024,
        temperature=1,  # 生成する応答の多様性
        presence_penalty=0,
        frequency_penalty=0,
        logit_bias={},
        user=userIdentifier
    )
    print(chatGPTResponse)

    say(chatGPTResponse["choices"][0]["message"]["content"])
