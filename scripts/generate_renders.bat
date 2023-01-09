FOR /L %%y IN (0, 1, 1000) DO (
cd "C:\Users\Jules\PycharmProjects\seasy_challenge"
"C:\Users\Jules\anaconda3\condabin\conda.bat" deactivate
"C:\Users\Jules\anaconda3\condabin\conda.bat" activate seasy_challenge
"C:\Users\Jules\anaconda3\envs\seasy_challenge\Scripts\blenderproc.exe" run data_generation/render.py)