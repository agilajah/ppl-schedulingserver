class MatKulOnlyTime
  def initialize(idmatkul)
    @idmatkul = idmatkul
    @r_selected = -1
    @j_selected = -1
    @h_selected = -1
    @sks = -1
  end

  def setTime(r, j, h, s)
    @r_selected = int(r)
    @j_selected = int(j)
    @h_selected = int(h)
    @sks = int(s)
  end

  def prin
    puts 'Ruang : ' + @r_selected
    puts 'Hari : ' + @h_selected
    puts 'Jam Mulai : ' + @j_selected
    puts 'SKS : ' + @sks
  end

end