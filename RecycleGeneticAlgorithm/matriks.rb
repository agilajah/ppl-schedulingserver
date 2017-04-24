class Matriks
  row = 0
  col = 0

  def initialize(r = None, c = None)

    if (r != None)
      @row = r
    end

    if (c != None)
      @col = c
    end

    @matriks = []
    for i in range(@row)
      matriks.append([])
      for j in range(@col)
        self.matriks[i].append([])
      end
    end

  end


    def conflict_count

      total = 0
      for ruang in @matriks
        for jam in ruang
          cnt = len(jam)
          total += cnt * (cnt-1) / 2
        end
      end
      return total

    end

    def prin
      puts (@row + ' ' + @col + ' ' + @matriks)
    end

  end
